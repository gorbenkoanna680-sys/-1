import streamlit as st 
import pandas as pd
import time
from scapy.all import IP, TCP, send

# --- Налаштування сторінки ---
st.set_page_config(
    page_title="DoS Attack Simulator",
    layout="wide",
    page_icon="🛡️"
)

# --- Кастомні стилі ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: #e2e8f0;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    .block-container {
        padding-top: 2rem;
    }

    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        transition: 0.3s ease;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    }

    .stButton>button {
        border-radius: 12px;
        padding: 10px 18px;
        font-weight: 600;
        transition: 0.3s;
    }

    .stButton>button:hover {
        transform: scale(1.05);
    }

    </style>
""", unsafe_allow_html=True)

# --- Заголовок ---
st.title("🛡️ Моделювання DoS-атаки")
st.caption("Симуляція навантаження та аналіз мережевих метрик у реальному часі")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Параметри атаки")

    target_ip = st.text_input("IP-адреса цілі", "127.0.0.1")
    port = st.number_input("Порт", value=80)
    intensity = st.slider("Інтенсивність (пакетів/сек)", 1, 100, 10)

# --- Session state ---
if 'stats' not in st.session_state:
    st.session_state.stats = pd.DataFrame(columns=['Time', 'Latency'])

# --- Функція атаки ---
def run_attack(ip, dport):
    packet = IP(dst=ip)/TCP(dport=dport, flags="S")
    send(packet, verbose=False)

# --- Layout ---
col1, col2 = st.columns([1, 2], gap="large")

# --- КЕРУВАННЯ ---
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎛️ Керування")

    btn_start = st.button("🚀 Запустити атаку", use_container_width=True)
    btn_stop = st.button("🛑 Зупинити", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- МЕТРИКИ ---
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📈 Метрики в реальному часі")

    chart_placeholder = st.empty()

    st.markdown('</div>', unsafe_allow_html=True)

# --- ЛОГІКА ---
if btn_start:
    st.toast(f"Атака на {target_ip} запущена", icon="⚡")

    for i in range(10):
        new_data = pd.DataFrame({
            'Time': [time.strftime("%H:%M:%S")],
            'Latency': [20 + (i * intensity)]
        })

        st.session_state.stats = pd.concat(
            [st.session_state.stats, new_data],
            ignore_index=True
        )

        chart_placeholder.line_chart(
            st.session_state.stats.set_index('Time'),
            use_container_width=True
        )

        # run_attack(target_ip, port)
        time.sleep(0.5)

    st.success("✅ Експеримент завершено. Дані зібрано.")

# --- ЕКСПОРТ ---
st.markdown("---")
st.download_button(
    label="📊 Завантажити результати (CSV)",
    data=st.session_state.stats.to_csv().encode('utf-8'),
    file_name='dos_results.csv',
    mime='text/csv',
    use_container_width=True
)
