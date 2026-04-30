import streamlit as st
import pandas as pd
import time
import random
from sklearn.ensemble import IsolationForest
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import requests

# ---------------- AUTH ----------------
USER = "admin"
PASS = "1234"

def login():
    st.title("🔐 CyberSOC Login")
    username = st.text_input("Login")
    password = st.text_input("Password", type="password")

    if st.button("Увійти"):
        if username == USER and password == PASS:
            st.session_state.auth = True
        else:
            st.error("Невірні дані")

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    login()
    st.stop()

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CyberSOC Cloud", layout="wide")
st.title("🛡️ CyberSOC Dashboard (Cloud Version)")
st.caption("Симуляція трафіку + ML аналіз аномалій")

# ---------------- TELEGRAM ----------------
TELEGRAM_TOKEN = st.secrets.get("TELEGRAM_TOKEN", "")
CHAT_ID = st.secrets.get("CHAT_ID", "")

def send_telegram(msg):
    if TELEGRAM_TOKEN and CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": msg}
            )
        except:
            pass

# ---------------- STATE ----------------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["latency"])

if "logs" not in st.session_state:
    st.session_state.logs = []

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Налаштування")

    intensity = st.slider("Інтенсивність трафіку", 1, 100, 10)
    sensitivity = st.slider("Чутливість IDS", 1, 100, 50)

# ---------------- ML ----------------
model = IsolationForest(contamination=0.1)

def detect_anomaly():
    if len(st.session_state.data) > 10:
        model.fit(st.session_state.data)
        preds = model.predict(st.session_state.data)

        if preds[-1] == -1:
            latency = st.session_state.data.iloc[-1][0]
            msg = f"🚨 Аномалія: latency {latency} ms"

            st.session_state.logs.append(msg)
            send_telegram(msg)

# ---------------- METRICS ----------------
m1, m2, m3, m4 = st.columns(4)

m1.metric("📦 Traffic", f"{intensity * random.randint(5,15)} pkt/s")
m2.metric("⏱ Latency", f"{random.randint(20,150)} ms")
m3.metric("🚨 Alerts", len(st.session_state.logs))
m4.metric("🌐 Active IP", random.randint(5, 50))

st.markdown("---")

# ---------------- UI ----------------
left, right = st.columns([2, 1])

with left:
    st.subheader("📈 Network Activity")
    chart = st.empty()

with right:
    start = st.button("🚀 Start Monitoring", use_container_width=True)
    stop = st.button("🛑 Stop", use_container_width=True)

    st.subheader("📜 Logs")
    log_box = st.empty()

# ---------------- MAIN LOOP ----------------
if start:
    st.success("Моніторинг запущено")

    for i in range(30):
        latency = 20 + i * intensity + random.randint(0, 40)

        new_data = pd.DataFrame({"latency": [latency]})
        st.session_state.data = pd.concat(
            [st.session_state.data, new_data],
            ignore_index=True
        )

        detect_anomaly()

        chart.line_chart(st.session_state.data)

        log_box.write(st.session_state.logs[-6:])

        time.sleep(0.4)

    st.success("Моніторинг завершено")

# ---------------- PDF ----------------
def generate_pdf():
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = [Paragraph("CyberSOC Report", styles["Title"])]

    for log in st.session_state.logs:
        content.append(Paragraph(log, styles["Normal"]))

    doc.build(content)

if st.button("🧾 Generate PDF"):
    generate_pdf()

    with open("report.pdf", "rb") as f:
        st.download_button("📥 Download PDF", f, "report.pdf")
