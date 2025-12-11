
import pandas as pd
import numpy as np
import os
from prophet import Prophet
import networkx as nx
from math import radians, sin, cos, sqrt, atan2
FILE = "your_data.csv"   
DEFAULT_FILE = "/mnt/data/trade_route_template.csv"

def load_data():
    if os.path.exists(FILE):
        print(f"[OK] Loading user dataset: {FILE}")
        return pd.read_csv(FILE)
    elif os.path.exists(DEFAULT_FILE):
        print("[WARNING] User file missing. Using template dataset.")
        return pd.read_csv(DEFAULT_FILE)
    else:
        raise FileNotFoundError("No CSV found. Upload a dataset first.")

df = load_data()
print("\nLoaded Data:")
display(df.head())


forecast_results = {}

for country in df["country"]:
    # generate fake 24-month series
    hist = pd.DataFrame({
        "ds": pd.date_range(start="2023-01-01", periods=24, freq="ME"),
        "y": np.linspace(50000, 90000, 24) + np.random.randint(-5000,5000,24)
    })

    model = Prophet()
    model.fit(hist)

    future = model.make_future_dataframe(periods=6, freq="ME")
    pred = model.predict(future)

    # Save future prediction (last value)
    next_price = float(pred.iloc[-1]["yhat"])
    forecast_results[country] = next_price

print("\nPredicted Prices:")
for c, p in forecast_results.items():
    print(f"{c}: {int(p)}")

# ---------------------- DISTANCE CALCULATOR ----------------------
def calc_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c  # km

# ---------------------- BUILD TRADE NETWORK ----------------------
G = nx.Graph()

for i, row1 in df.iterrows():
    for j, row2 in df.iterrows():
        if i < j:
            dist = calc_distance(row1.lat, row1.lon, row2.lat, row2.lon)
            G.add_edge(row1.country, row2.country, weight=dist)

# ---------------------- FIND SHORTEST PATH ----------------------
countries = df["country"].tolist()

if "India" in countries and "USA" in countries:
    best_route = nx.shortest_path(G, source="India", target="USA", weight="weight")
else:
    best_route = ["Path not possible with given dataset"]

# ---------------------- RISK ANALYSIS ----------------------
usa_risk = float(df[df["country"]=="USA"]["risk_score"].iloc[0]) if "USA" in df.country.tolist() else None

if usa_risk is None:
    risk_level = "Unknown"
elif usa_risk < 3:
    risk_level = "Low"
elif usa_risk < 6:
    risk_level = "Medium"
else:
    risk_level = "High"

# ---------------------- FINAL OUTPUT ----------------------
output = {
    "Predicted Prices": forecast_results,
    "Best Route India → USA": best_route,
    "USA Risk Score": usa_risk,
    "Risk Level": risk_level
}

print("\n\n===== FINAL AI TRADE SYSTEM OUTPUT =====")
output
