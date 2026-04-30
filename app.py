import streamlit as st
import pandas as pd
import time
import random
from scapy.all import IP, TCP, send

# --- CONFIG ---
st.set_page_config(
    page_title="Cyber Security Dashboard",
    layout="wide",
    page_icon="🛡️"
)

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
    box-shadow: 0 0 25px rgba(0,0,0,0.4);
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-4px);
}

.stMetric {
    background: rgba(255,255,255,0.03);
    padding: 10px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ Cyber Security Monitoring Dashboard")
st.caption("Моніторинг мережевої активності та симуляція DoS-атаки")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Налаштування")

    target_ip = st.text_input("Target IP", "127.0.0.1")
    port = st.number_input("Port", value=80)
    intensity = st.slider("Інтенсивність", 1, 100, 10)

    st.markdown("---")
    st.subheader("📡 Стан системи")
    system_status = st.radio("Статус:", ["🟢 Норма", "🟡 Підозра", "🔴 Атака"])

# --- STATE ---
if "stats" not in st.session_state:
    st.session_state.stats = pd.DataFrame(columns=["Time", "Latency"])

if "logs" not in st.session_state:
    st.session_state.logs = []

# --- ATTACK FUNCTION ---
def run_attack(ip, dport):
    packet = IP(dst=ip)/TCP(dport=dport, flags="S")
    send(packet, verbose=False)

# --- TOP METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Пакети/сек", intensity)

with col2:
    st.metric("⏱️ Затримка", f"{random.randint(20,120)} ms")

with col3:
    st.metric("🚨 Загрози", len(st.session_state.logs))

with col4:
    st.metric("🌐 Активні IP", random.randint(1, 20))

st.markdown("---")

# --- MAIN LAYOUT ---
left, right = st.columns([2, 1], gap="large")

# --- GRAPH ---
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Мережеві метрики")

    chart = st.empty()

    st.markdown('</div>', unsafe_allow_html=True)

# --- CONTROL PANEL ---
with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎛️ Управління")

    start = st.button("🚀 Start Attack", use_container_width=True)
    stop = st.button("🛑 Stop", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📜 Логи подій")

    log_box = st.empty()

    st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIC ---
if start:
    st.toast("Атака запущена ⚡")

    for i in range(15):
        latency = 20 + i * intensity + random.randint(0, 30)

        new_data = pd.DataFrame({
            "Time": [time.strftime("%H:%M:%S")],
            "Latency": [latency]
        })

        st.session_state.stats = pd.concat(
            [st.session_state.stats, new_data],
            ignore_index=True
        )

        # --- LOG GENERATION ---
        if latency > 100:
            event = f"🚨 HIGH LATENCY DETECTED: {latency} ms"
            st.session_state.logs.append(event)

        # --- UPDATE GRAPH ---
        chart.line_chart(
            st.session_state.stats.set_index("Time"),
            use_container_width=True
        )

        # --- UPDATE LOGS ---
        log_box.write(st.session_state.logs[-5:])

        # run_attack(target_ip, port)
        time.sleep(0.5)

    st.success("Атака завершена")

# --- DOWNLOAD ---
st.markdown("---")
st.download_button(
    "📊 Завантажити CSV",
    st.session_state.stats.to_csv().encode("utf-8"),
    "report.csv",
    "text/csv",
    use_container_width=True
)
