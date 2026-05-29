import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import time
import random

# Налаштування сторінки
st.set_page_config(page_title="CyberSOC Graph Edition", layout="wide")

# Стилізація
st.markdown("""
<style>
.main { background: linear-gradient(135deg, #020617, #0f172a); color: #e2e8f0; }
.card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 16px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ CyberSOC Monitoring System (Graph Analysis)")
st.caption("Моделювання топології мережі, аналіз відмов та DoS-сценаріїв через теорію графів")

# ----------------- СТВОРЕННЯ БАЗОВОЇ ТОПОЛОГІЇ МЕРЕЖІ -----------------
def create_base_network():
    G = nx.Graph()
    # Додаємо вузли з їхніми початковими статусами
    nodes = {
        "Client": {"type": "host", "status": "active"},
        "Switch": {"type": "equipment", "status": "active"},
        "Router-1": {"type": "router", "status": "active"},
        "Router-2": {"type": "router", "status": "active"},
        "Firewall": {"type": "security", "status": "active"},
        "Web Server": {"type": "server", "status": "active"}
    }
    for node, attrs in nodes.items():
        G.add_node(node, **attrs)
    
    # Додаємо ребра (канали зв'язку) з базовою вагою (затримкою в мс)
    edges = [
        ("Client", "Switch", 5),
        ("Switch", "Router-1", 10),
        ("Switch", "Router-2", 15),
        ("Router-1", "Firewall", 10),
        ("Router-2", "Firewall", 20),
        ("Firewall", "Web Server", 5)
    ]
    G.add_weighted_edges_from(edges)
    return G

# Ініціалізація стану сесії
if "logs" not in st.session_state:
    st.session_state.logs = ["Систему ініціалізовано. Мережа стабільна."]
if "stats" not in st.session_state:
    st.session_state.stats = pd.DataFrame(columns=["Time", "Latency"])

# ----------------- БІЧНА ПАНЕЛЬ КЕРУВАННЯ -----------------
with st.sidebar:
    st.header("⚙️ Налаштування симуляції")
    
    # Вибір вузла та типу відмови/атаки
    target_node = st.selectbox("Оберіть цільовий вузол мережі:", ["Web Server", "Router-1", "Firewall", "Router-2", "Switch", "Client"])
    attack_type = st.selectbox("Тип впливу / Атаки:", [
        "Нормальний режим (Без атак)",
        "Сценарій 1: DoS на Web Server",
        "Сценарій 2: Перевантаження Router-1",
        "Сценарій 3: Відключення Firewall",
        "Сценарій 4: Розрив каналу зв'язку"
    ])
    
    intensity = st.slider("Інтенсивність атаки (Traffic Load)", 1, 100, 10)
    st.markdown("---")
    st.subheader("🧠 Налаштування IDS")
    sensitivity = st.slider("Чутливість виявлення аномалій", 1, 100, 50)
    
    st.markdown("---")
    start = st.button("🚀 Запустити моделювання", use_container_width=True)

# ----------------- МОДЕЛЮВАННЯ ВПЛИВУ АТАК НА ГРАФ -----------------
G = create_base_network()
current_logs = []

if attack_type == "Сценарій 1: DoS на Web Server":
    # Результат: Збільшення затримки на сервері пропорційно інтенсивності
    extra_delay = intensity * 5
    G.nodes["Web Server"]["status"] = "overloaded"
    for neighbor in G.neighbors("Web Server"):
        G["Web Server"][neighbor]["weight"] += extra_delay
    current_logs.append(f"🚨 ALERT: Зафіксовано DoS-атаку на Web Server! Затримка зросла на +{extra_delay}мс.")

elif attack_type == "Сценарій 2: Перевантаження Router-1":
    # Результат: Перевантаження роутера, трафік іде в обхід через Router-2
    G.nodes["Router-1"]["status"] = "overloaded"
    for neighbor in G.neighbors("Router-1"):
        G["Router-1"][neighbor]["weight"] += (intensity * 10)
    current_logs.append("⚠️ WARNING: Router-1 перевантажено аномальним трафіком. Маршрутизація ускладнена.")

elif attack_type == "Сценарій 3: Відключення Firewall":
    # Результат: Видалення вузла, граф розпадається на ізольовані компоненти
    G.remove_node("Firewall")
    current_logs.append("🔥 CRITICAL: Firewall повністю відключено / атаковано! Мережу розірвано.")

elif attack_type == "Сценарій 4: Розрив каналу зв'язку":
    # Результат: Видалення ребра між Switch та Router-1
    if G.has_edge("Switch", "Router-1"):
        G.remove_edge("Switch", "Router-1")
    current_logs.append("❌ ALERT: Зафіксовано фізичний розрив каналу 'Switch <--> Router-1'.")

# Збереження логів у сесію
if start and current_logs:
    st.session_state.logs.extend(current_logs)

# ----------------- ОБЧИСЛЕННЯ ХАРАКТЕРИСТИК ГРАФА -----------------
num_nodes = G.number_of_nodes()
num_edges = G.number_of_edges()
density = nx.density(G)
avg_degree = sum(dict(G.degree()).values()) / num_nodes if num_nodes > 0 else 0
components = nx.number_connected_components(G) if num_nodes > 0 else 0

# Розрахунок центральності вузлів (Betweenness Centrality)
centrality = nx.betweenness_centrality(G) if num_nodes > 2 else {}

# Розрахунок найкоротшого шляху (Дейкстра) між Client та Web Server
has_path = False
path_nodes = []
path_latency = 0

if "Client" in G and "Web Server" in G:
    try:
        path_nodes = nx.shortest_path(G, source="Client", target="Web Server", weight="weight")
        path_latency = nx.shortest_path_length(G, source="Client", target="Web Server", weight="weight")
        has_path = True
    except nx.NetworkXNoPath:
        has_path = False

# Оновлення графіку затримок для IDS дашборду
if start and has_path:
    new_stat = pd.DataFrame({"Time": [time.strftime("%H:%M:%S")], "Latency": [path_latency]})
    st.session_state.stats = pd.concat([st.session_state.stats, new_stat], ignore_index=True)

# ----------------- ВІДОБРАЖЕННЯ ВІДЖЕТІВ ТА МЕТРИК -----------------
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("📦 Поточний Шлях (Дейкстра)", " -> ".join(path_nodes) if has_path else "НЕМАЄ ЗВ'ЯЗКУ")
col_m2.metric("⏱ Latency (Client -> Server)", f"{path_latency} ms" if has_path else "∞ (НЕДОСТУПНО)")
col_m3.metric("🚨 Компонент зв'язності", f"{components} (Граф розпався!)" if components > 1 else f"{components}")
col_m4.metric("📊 Щільність графа", f"{density:.2f}")

st.markdown("---")

# ХАРАКТЕРИСТИКИ ГРАФА (Пункт 2)
st.subheader("📊 Основні характеристики та метрики графа мережі")
col_char1, col_char2, col_char3 = st.columns(3)
with col_char1:
    st.write(f"**Кількість вузлів:** {num_nodes}")
    st.write(f"**Кількість ребер:** {num_edges}")
with col_char2:
    st.write(f"**Середній ступінь вершин:** {avg_degree:.2f}")
    st.write(f"**Стан зв'язності:** " + ("Мережа розділена" if components > 1 else "Мережа цілісна"))
with col_char3:
    st.write("**Центральність вузлів (Betweenness Centrality):**")
    for node, cent in centrality.items():
        st.write(f"- {node}: `{cent:.3f}`")

st.markdown("---")

# ----------------- ВІЗУАЛІЗАЦІЯ ГРАФА (Пункт 8) -----------------
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("🌐 Візуалізація топології та змін після атаки")
    
    if num_nodes > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        # Фіксоване розміщення вузлів для красивого відображення
        fixed_pos = {
            "Client": (0, 1),
            "Switch": (1, 1),
            "Router-1": (2, 2),
            "Router-2": (2, 0),
            "Firewall": (3, 1),
            "Web Server": (4, 1)
        }
        # Залишаємо позиції тільки для тих вузлів, які є в графі
        pos = {node: fixed_pos[node] for node in G.nodes()}
        
        # Визначаємо кольори вузлів на основі стану
        node_colors = []
        for node in G.nodes():
            if G.nodes[node].get("status") == "overloaded":
                node_colors.append("#ef4444")  # Червоний (перевантажений)
            elif node in path_nodes:
                node_colors.append("#22c55e")  # Зелений (активний маршрут)
            else:
                node_colors.append("#3b82f6")  # Синій (звичайний активний)
        
        # Малюємо вузли та ребра
        nx.draw_networkx_nodes(G, pos, node_size=1200, node_color=node_colors, ax=ax)
        nx.draw_networkx_labels(G, pos, font_color="white", font_weight="bold", font_size=10, ax=ax)
        
        # Підсвічуємо ребра, які входять в Shortest Path Дейкстри
        edge_colors = []
        edge_widths = []
        path_edges = list(zip(path_nodes, path_nodes[1:])) if has_path else []
        
        for u, v in G.edges():
            if (u, v) in path_edges or (v, u) in path_edges:
                edge_colors.append("#22c55e")  # Зелений маршрут Дейкстри
                edge_widths.append(4)
            else:
                edge_colors.append("#64748b")  # Сірий звичайний кабель
                edge_widths.append(2)
                
        nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, ax=ax)
        
        # Додаємо підписи ваг ребер (затримок)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, ax=ax)
        
        fig.patch.set_facecolor('#0f172a')
        ax.set_facecolor('#0f172a')
        plt.axis('off')
        st.pyplot(fig)
    else:
        st.error("Граф порожній.")

with right_col:
    st.subheader("📜 Системний журнал SOC (Logs)")
    # Показуємо останні 8 подій
    for log in st.session_state.logs[-8:][::-1]:
        st.write(log)
        
    st.markdown("---")
    # Перевірка порогу аномалії IDS
    threshold = 50 + sensitivity
    if has_path and path_latency > threshold:
        st.error(f"🚨 IDS ALERT: Виявлено критичну аномалію! Latency ({path_latency}мс) перевищує поріг ({threshold}мс).")
    elif not has_path:
        st.error("🚨 IDS CRITICAL: ВУЗОЛ ВЕБ-СЕРВЕРА НЕДОСТУПНИЙ (Повна відмова в обслуговуванні)!")
    else:
        st.success("✅ IDS: Трафік у межах норми.")

# Експорт результатів у CSV
st.markdown("---")
st.download_button(
    "📊 Експорт логів у CSV",
    pd.DataFrame(st.session_state.logs, columns=["SOC_Log_Event"]).to_csv().encode("utf-8"),
    "cyber_graph_report.csv",
    "text/csv",
    use_container_width=True
)
