import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import requests, polyline, ollama

# ---------------- CONFIG ----------------
st.set_page_config(page_title="GTORIS PRO", layout="wide")

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjRlOWQwOTIyNWM1YjRjYjFiZGY0NzI4ODc4YmU0NzU1IiwiaCI6Im11cm11cjY0In0="  # 🔑 PUT YOUR ORS KEY HERE

st.title("🌍 GTORIS — AI Travel Intelligence")

# ---------------- INDIA STATES ----------------
india = {
    "Andhra Pradesh": ["Visakhapatnam","Vijayawada"],
    "Arunachal Pradesh": ["Itanagar"],
    "Assam": ["Guwahati"],
    "Bihar": ["Patna","Gaya"],
    "Chhattisgarh": ["Raipur"],
    "Goa": ["Panaji"],
    "Gujarat": ["Ahmedabad","Surat"],
    "Haryana": ["Gurgaon"],
    "Himachal Pradesh": ["Shimla"],
    "Jharkhand": ["Ranchi"],
    "Karnataka": ["Bangalore","Mysore"],
    "Kerala": ["Kochi","Trivandrum"],
    "Madhya Pradesh": ["Bhopal","Indore"],
    "Maharashtra": ["Mumbai","Pune","Nagpur"],
    "Manipur": ["Imphal"],
    "Meghalaya": ["Shillong"],
    "Mizoram": ["Aizawl"],
    "Nagaland": ["Kohima"],
    "Odisha": ["Bhubaneswar"],
    "Punjab": ["Amritsar"],
    "Rajasthan": ["Jaipur","Udaipur"],
    "Sikkim": ["Gangtok"],
    "Tamil Nadu": ["Chennai","Madurai"],
    "Telangana": ["Hyderabad"],
    "Tripura": ["Agartala"],
    "Uttar Pradesh": ["Lucknow","Varanasi"],
    "Uttarakhand": ["Dehradun"],
    "West Bengal": ["Kolkata"],
    "Delhi": ["New Delhi"]
}

coords = {
    "Mumbai":(19.0760,72.8777),"Pune":(18.5204,73.8567),"Nagpur":(21.1458,79.0882),
    "Bangalore":(12.9716,77.5946),"Mysore":(12.2958,76.6394),
    "Chennai":(13.0827,80.2707),"Madurai":(9.9252,78.1198),
    "Lucknow":(26.8467,80.9462),"Varanasi":(25.3176,82.9739),
    "New Delhi":(28.6139,77.2090),
    "Ahmedabad":(23.0225,72.5714),"Surat":(21.1702,72.8311),
    "Jaipur":(26.9124,75.7873),"Udaipur":(24.5854,73.7125),
    "Kolkata":(22.5726,88.3639),
    "Patna":(25.5941,85.1376),"Gaya":(24.7955,85.0002),
    "Hyderabad":(17.3850,78.4867),
    "Kochi":(9.9312,76.2673),"Trivandrum":(8.5241,76.9366),
    "Guwahati":(26.1445,91.7362),"Itanagar":(27.0844,93.6053),
    "Raipur":(21.2514,81.6296),"Panaji":(15.4909,73.8278),
    "Gurgaon":(28.4595,77.0266),"Shimla":(31.1048,77.1734),
    "Ranchi":(23.3441,85.3096),"Bhopal":(23.2599,77.4126),
    "Imphal":(24.8170,93.9368),"Shillong":(25.5788,91.8933),
    "Aizawl":(23.7271,92.7176),"Kohima":(25.6747,94.1100),
    "Bhubaneswar":(20.2961,85.8245),"Amritsar":(31.6340,74.8723),
    "Gangtok":(27.3389,88.6065),"Agartala":(23.8315,91.2868),
    "Dehradun":(30.3165,78.0322)
}

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    s_state = st.selectbox("Source State", list(india.keys()))
    s_city = st.selectbox("Source City", india[s_state])

with col2:
    d_state = st.selectbox("Destination State", list(india.keys()))
    d_city = st.selectbox("Destination City", india[d_state])

# ---------------- FUNCTIONS ----------------
def distance(a,b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)*111

def get_route(c1,c2):
    if not ORS_API_KEY:
        return None
    try:
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {"Authorization": ORS_API_KEY}
        body = {"coordinates": [[c1[1],c1[0]],[c2[1],c2[0]]]}
        res = requests.post(url,json=body,headers=headers)
        geometry = res.json()["routes"][0]["geometry"]
        return polyline.decode(geometry)
    except:
        return None

def estimate_modes(d):
    return {
        "Car": {"Time": round(d/60,2), "Cost": int(d*12)},
        "Train": {"Time": round(d/70,2), "Cost": int(d*1.5)},
        "Flight": {"Time": round(d/500+2,2), "Cost": int(d*4)}
    }

# ---------------- OLLAMA AI ----------------
def ollama_ai(query, best):
    prompt = f"""
You are Ava, a smart female AI travel assistant.

Trip:
Distance: {round(best['Distance'])} km
Cost: ₹{best['Cost']}
Time: {best['Time']} hrs

Answer naturally and intelligently.

User: {query}
"""
    try:
        res = ollama.chat(
            model="llama3",
            messages=[{"role":"user","content":prompt}]
        )
        return res["message"]["content"]
    except:
        return "⚠️ Start Ollama: ollama run llama3"

# ---------------- MAIN ----------------
if st.button("Analyze"):

    c1 = coords[s_city]
    c2 = coords[d_city]

    d = distance(c1,c2)

    st.session_state.best = {
        "Distance": d,
        "Cost": int(d*12),
        "Time": round(d/60,2)
    }

    st.session_state.coords = (c1,c2)

# ---------------- DISPLAY ----------------
if "best" in st.session_state:

    best = st.session_state.best
    c1,c2 = st.session_state.coords

    st.subheader("🏆 Travel Plan")

    c1m,c2m,c3m = st.columns(3)
    c1m.metric("Cost", f"₹{best['Cost']}")
    c2m.metric("Distance", f"{round(best['Distance'])} km")
    c3m.metric("Time", f"{best['Time']} hr")

    st.subheader("🚀 Transport")
    st.dataframe(pd.DataFrame(estimate_modes(best["Distance"])).T)

    st.subheader("🗺 Route Map")
    m = folium.Map(location=[c1[0],c1[1]], zoom_start=5)

    route = get_route(c1,c2)

    if route:
        folium.PolyLine(route,color="blue",weight=5).add_to(m)
    else:
        folium.PolyLine([c1,c2],color="red").add_to(m)
        st.warning("Add ORS key for real route")

    folium.Marker(c1).add_to(m)
    folium.Marker(c2).add_to(m)

    st_folium(m,width=900)

# ---------------- AI CHAT ----------------
st.subheader("🤖 Ava — AI Assistant")

if "chat" not in st.session_state:
    st.session_state.chat = []

q = st.text_input("Ask anything")

if st.button("Ask AI") and q:

    if "best" not in st.session_state:
        st.warning("Run analysis first")
    else:
        ans = ollama_ai(q, st.session_state.best)
        st.session_state.chat.append(("You", q))
        st.session_state.chat.append(("Ava", ans))

for role,msg in st.session_state.chat:
    st.write(f"**{role}:** {msg}")
