import streamlit as st
import pandas as pd
import time
import random
from sklearn.ensemble import IsolationForest
from scapy.all import sniff
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import requests

# ---------------- AUTH ----------------
USER = "admin"
PASS = "1234"

def login():
    st.title("🔐 Login")
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
st.set_page_config(page_title="CyberSOC", layout="wide")
st.title("🛡️ CyberSOC Dashboard")

# ---------------- TELEGRAM ----------------
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

def send_telegram(msg):
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

# ---------------- ML MODEL ----------------
model = IsolationForest(contamination=0.1)

# ---------------- PACKET SNIFF ----------------
def process_packet(pkt):
    latency = random.randint(20, 200)  # імітація
    st.session_state.data.loc[len(st.session_state.data)] = [latency]

# ---------------- UI ----------------
col1, col2, col3 = st.columns(3)

col1.metric("📦 Traffic", random.randint(50, 500))
col2.metric("⏱ Latency", random.randint(20, 200))
col3.metric("🚨 Alerts", len(st.session_state.logs))

start = st.button("🚀 Start Monitoring")

chart = st.empty()
logs_box = st.empty()

# ---------------- MAIN ----------------
if start:
    st.success("Моніторинг запущено")

    for i in range(30):

        # sniff пакетів (обмежено 1 пакет)
        sniff(prn=process_packet, count=1, store=0)

        if len(st.session_state.data) > 10:
            model.fit(st.session_state.data)
            preds = model.predict(st.session_state.data)

            if preds[-1] == -1:
                msg = f"🚨 Anomaly detected: {st.session_state.data.iloc[-1][0]}"
                st.session_state.logs.append(msg)

                send_telegram(msg)

        chart.line_chart(st.session_state.data)

        logs_box.write(st.session_state.logs[-5:])

        time.sleep(0.3)

# ---------------- PDF REPORT ----------------
def generate_pdf():
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("CyberSOC Report", styles["Title"]))

    for log in st.session_state.logs:
        content.append(Paragraph(log, styles["Normal"]))

    doc.build(content)

if st.button("🧾 Generate PDF"):
    generate_pdf()
    with open("report.pdf", "rb") as f:
        st.download_button("📥 Download PDF", f, "report.pdf")
