import streamlit as st
import pandas as pd
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="CyberSOC Dashboard", layout="wide")

# --- STYLES ---
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e2e8f0;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 20px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ CyberSOC Monitoring System")
st.caption("Аналіз мережевої активності, IDS та виявлення аномалій")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Налаштування")
    intensity = st.slider("Інтенсивність трафіку", 1, 100, 10)

    st.markdown("---")
    st.subheader("🧠 IDS режим")
    sensitivity = st.slider("Чутливість", 1, 100, 50)

# --- STATE ---
if "stats" not in st.session_state:
    st.session_state.stats = pd.DataFrame(columns=["Time", "Latency"])

if "logs" not in st.session_state:
    st.session_state.logs = []

if "map_data" not in st.session_state:
    st.session_state.map_data = pd.DataFrame(columns=["lat", "lon"])

# --- IDS LOGIC ---
def detect_anomaly(latency, sensitivity):
    threshold = 50 + sensitivity
    return latency > threshold

# --- METRICS ---
m1, m2, m3, m4 = st.columns(4)

m1.metric("📦 Traffic", f"{intensity * random.randint(5,15)} pkt/s")
m2.metric("⏱ Latency", f"{random.randint(20,150)} ms")
m3.metric("🚨 Alerts", len(st.session_state.logs))
m4.metric("🌐 IP Active", random.randint(5, 50))

st.markdown("---")

# --- LAYOUT ---
left, right = st.columns([2, 1])

# --- GRAPH ---
with left:
    st.subheader("📈 Network Activity")
    chart = st.empty()

    st.subheader("🌍 Attack Map (simulation)")
    map_placeholder = st.empty()

# --- CONTROL + LOGS ---
with right:
    start = st.button("🚀 Start Monitoring", use_container_width=True)
    stop = st.button("🛑 Stop", use_container_width=True)

    st.subheader("📜 Logs")
    log_box = st.empty()

# --- MAIN LOOP ---
if start:
    st.toast("Моніторинг запущено")

    for i in range(20):
        latency = 20 + i * intensity + random.randint(0, 50)

        new_data = pd.DataFrame({
            "Time": [time.strftime("%H:%M:%S")],
            "Latency": [latency]
        })

        st.session_state.stats = pd.concat(
            [st.session_state.stats, new_data],
            ignore_index=True
        )

        # --- IDS DETECTION ---
        if detect_anomaly(latency, sensitivity):
            event = f"🚨 ALERT: anomaly latency {latency} ms"
            st.session_state.logs.append(event)

            # --- ADD RANDOM GEO POINT ---
            lat = random.uniform(-90, 90)
            lon = random.uniform(-180, 180)

            new_point = pd.DataFrame({"lat": [lat], "lon": [lon]})
            st.session_state.map_data = pd.concat(
                [st.session_state.map_data, new_point],
                ignore_index=True
            )

        # --- UPDATE GRAPH ---
        chart.line_chart(
            st.session_state.stats.set_index("Time"),
            use_container_width=True
        )

        # --- UPDATE MAP ---
        if not st.session_state.map_data.empty:
            map_placeholder.map(st.session_state.map_data)

        # --- UPDATE LOGS ---
        log_box.write(st.session_state.logs[-8:])

        time.sleep(0.4)

    st.success("Моніторинг завершено")

# --- DOWNLOAD ---
st.markdown("---")
st.download_button(
    "📊 Export CSV",
    st.session_state.stats.to_csv().encode("utf-8"),
    "cyber_report.csv",
    "text/csv",
    use_container_width=True
)
