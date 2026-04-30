import streamlit as st
import pandas as pd
import time
import threading
from scapy.all import IP, TCP, send

st.set_page_config(page_title="DoS Attack Simulator", layout="wide")

st.title("🛡️ Моделювання DoS-атаки та аналіз метрик")

# Налаштування в боковій панелі
st.sidebar.header("Параметри атаки")
target_ip = st.sidebar.text_input("IP-адреса цілі", "127.0.0.1")
port = st.sidebar.number_input("Порт", value=80)
intensity = st.sidebar.slider("Інтенсивність (пакетів/сек)", 1, 100, 10)

# Ініціалізація стану для логів
if 'stats' not in st.session_state:
    st.session_state.stats = pd.DataFrame(columns=['Time', 'Latency'])

# Функція атаки (спрощена для демонстрації)
def run_attack(ip, dport):
    packet = IP(dst=ip)/TCP(dport=dport, flags="S")
    send(packet, verbose=False)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Керування")
    btn_start = st.button("🚀 Запустити атаку")
    btn_stop = st.button("🛑 Зупинити")

with col2:
    st.subheader("Метрики реального часу")
    chart_placeholder = st.empty()

if btn_start:
    st.warning(f"Атака на {target_ip} запущена...")
    # У реальному Streamlit-додатку тут би запускався цикл
    # Для демонстрації додамо кілька точок даних
    for i in range(10):
        # Імітуємо зростання затримки
        new_data = pd.DataFrame({
            'Time': [time.strftime("%H:%M:%S")],
            'Latency': [20 + (i * intensity)] # Формула залежності
        })
        st.session_state.stats = pd.concat([st.session_state.stats, new_data], ignore_index=True)
        chart_placeholder.line_chart(st.session_state.stats.set_index('Time'))
        
        # Виклик функції Scapy (тільки локально з правами admin)
        # run_attack(target_ip, port) 
        
        time.sleep(0.5)
    st.success("Експеримент завершено. Дані зібрано.")

# Можливість завантажити звіт
st.download_button(
    label="📊 Завантажити результати у CSV",
    data=st.session_state.stats.to_csv().encode('utf-8'),
    file_name='dos_results.csv',
    mime='text/csv',
)