import streamlit as st
import random
import pandas as pd
import time
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Water Quality Monitoring",
    page_icon="💧",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "ph_history" not in st.session_state:
    st.session_state.ph_history = []
    st.session_state.turb_history = []
    st.session_state.tds_history = []
    st.session_state.alert_log = []

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Control Panel")

location = st.sidebar.selectbox(
    "📍 Monitoring Location",
    ["Narmada River", "Indore City", "Water Treatment Plant"]
)

refresh_time = st.sidebar.slider("⏱️ Auto Refresh (seconds)", 2, 10, 4)

demo_mode = st.sidebar.toggle("🎓 Demo Mode (Manual Control)")
simulate_spike = st.sidebar.button("🚨 Simulate Contamination")

with st.sidebar.expander("ℹ️ How this works"):
    st.write("""
    • Sensors are simulated using software  
    • Demo mode allows manual exploration  
    • Alerts trigger automatically  
    """)

# ---------------- HERO SECTION ----------------
st.markdown("""
<div style="
background: linear-gradient(90deg, #1CB5E0, #000851);
padding: 22px;
border-radius: 14px;
text-align: center;
color: white;
">
<h1>💧 Smart Water Quality Monitoring System</h1>
<p>Interactive smart city dashboard for real-time water safety</p>
</div>
""", unsafe_allow_html=True)

# ---------------- SENSOR VALUES ----------------
if demo_mode:
    ph = st.sidebar.slider("🧪 Adjust pH Level", 0.0, 14.0, 7.2)
    turbidity = st.sidebar.slider("🌫️ Adjust Turbidity (NTU)", 0.0, 10.0, 2.0)
    tds = st.sidebar.slider("🧂 Adjust TDS (ppm)", 0, 1200, 350)
elif simulate_spike:
    ph = round(random.uniform(3, 5), 2)
    turbidity = round(random.uniform(7, 10), 2)
    tds = random.randint(900, 1200)
else:
    ph = round(random.uniform(6.5, 8.8), 2)
    turbidity = round(random.uniform(0, 6), 2)
    tds = random.randint(100, 700)

# ---------------- STORE HISTORY ----------------
st.session_state.ph_history.append(ph)
st.session_state.turb_history.append(turbidity)
st.session_state.tds_history.append(tds)

st.session_state.ph_history = st.session_state.ph_history[-10:]
st.session_state.turb_history = st.session_state.turb_history[-10:]
st.session_state.tds_history = st.session_state.tds_history[-10:]

# ---------------- QUALITY LOGIC ----------------
def classify(ph, turb, tds):
    if 6.5 <= ph <= 8.5 and turb < 3 and tds <= 600:
        return "Safe"
    elif turb <= 5 and tds <= 900:
        return "Moderate"
    else:
        return "Unsafe"

status = classify(ph, turbidity, tds)

# ---------------- WQI ----------------
wqi = max(0, min(100, int(
    100 - (abs(7 - ph) * 10 + turbidity * 8 + (tds / 50))
)))

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Trends", "🚨 Alerts"])

# ---------------- DASHBOARD TAB ----------------
with tab1:
    st.subheader("🔬 Live Sensor Readings")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🧪 pH Level", ph)
    c2.metric("🌫️ Turbidity (NTU)", turbidity)
    c3.metric("🧂 TDS (ppm)", tds)
    c4.metric("📊 Water Quality Index", wqi)

    st.markdown("### 🚦 Water Safety Status")

    if status == "Safe":
        bg = "#d4edda"
        rec = "Safe for drinking and domestic use."
    elif status == "Moderate":
        bg = "#fff3cd"
        rec = "Boil water before drinking."
    else:
        bg = "#f8d7da"
        rec = "Do NOT consume. Inform authorities."

    st.markdown(f"""
    <div style="
    padding: 16px;
    border-radius: 12px;
    background-color: {bg};
    ">
    <h3>Status: {status}</h3>
    <p>{rec}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📊 Water Quality Indicator")
    st.progress(wqi)

# ---------------- TRENDS TAB ----------------
with tab2:
    st.subheader("📈 Sensor Trends (Last 10 Readings)")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.line_chart(pd.DataFrame({"pH": st.session_state.ph_history}), height=250)

    with col2:
        st.line_chart(pd.DataFrame({"Turbidity": st.session_state.turb_history}), height=250)

    with col3:
        st.line_chart(pd.DataFrame({"TDS": st.session_state.tds_history}), height=250)

# ---------------- ALERT TAB ----------------
with tab3:
    if status == "Unsafe":
        st.session_state.alert_log.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Location": location,
            "pH": ph,
            "Turbidity": turbidity,
            "TDS": tds
        })

    if st.session_state.alert_log:
        alert_df = pd.DataFrame(st.session_state.alert_log)
        st.dataframe(alert_df, use_container_width=True)

        st.download_button(
            "⬇️ Download Alert Report (CSV)",
            alert_df.to_csv(index=False),
            "water_alert_report.csv",
            "text/csv"
        )
    else:
        st.info("No unsafe alerts recorded yet.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption(f"🏆 Smart Indore Hackathon 2026 | Location: {location}")

# ---------------- AUTO REFRESH ----------------
time.sleep(refresh_time)
st.rerun()
