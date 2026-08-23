import streamlit as st
import pandas as pd
from datetime import datetime, time
from supabase import create_client, Client
import os

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Hotel Logbook",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS PERSONALIZADO - DARK THEME WALDORF ASTORIA STYLE
# ============================================================
st.markdown("""
<style>
    :root {
        --bg-primary: #0b0f14;
        --bg-secondary: #111820;
        --bg-card: #151c24;
        --bg-input: #1a2330;
        --border-color: #1e2a38;
        --accent: #00d4d4;
        --accent-hover: #00bbbb;
        --text-primary: #e8ecf1;
        --text-secondary: #8b9aae;
        --text-muted: #5a6b7d;
        --danger: #ff4757;
        --success: #2ed573;
    }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: var(--bg-primary) !important; }
    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color);
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100%; text-align: left; background: transparent; border: none;
        color: var(--text-secondary); font-size: 0.95rem; padding: 0.6rem 1rem;
        border-radius: 8px; transition: all 0.2s ease; margin-bottom: 0.3rem;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0, 212, 212, 0.08); color: var(--text-primary);
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: var(--accent) !important; color: #000 !important; font-weight: 600;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: var(--accent-hover) !important;
    }
    h1, h2, h3, h4, h5, h6 { color: var(--text-primary) !important; font-weight: 600 !important; }
    p, span, label { color: var(--text-secondary) !important; }
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input,
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input,
    .stSelectbox > div > div {
        background-color: var(--bg-input) !important; border: 1px solid var(--border-color) !important;
        border-radius: 8px !important; color: var(--text-primary) !important;
        padding: 0.6rem 0.8rem !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 212, 0.15) !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--accent) !important; color: #000 !important; border: none !important;
        border-radius: 8px !important; padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important; font-size: 1rem !important; transition: all 0.2s ease !important;
    }
    .stButton > button[kind="primary"]:hover { background: var(--accent-hover) !important; transform: translateY(-1px); }
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] {
        background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); padding: 1.5rem;
    }
    .stDataFrame {
        background: var(--bg-card) !important; border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
    }
    .stDataFrame th {
        background: var(--bg-secondary) !important; color: var(--text-primary) !important;
        font-weight: 600 !important; border-bottom: 1px solid var(--border-color) !important;
    }
    .stDataFrame td { color: var(--text-secondary) !important; border-bottom: 1px solid var(--border-color) !important; }
    .stDataFrame tr:hover td { background: rgba(0, 212, 212, 0.05) !important; }
    [data-testid="stMetricValue"] { color: var(--accent) !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: var(--bg-secondary); }
    ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
    .stAlert { background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; border-radius: 8px !important; }
    .stAlert [data-testid="stAlertContentSuccess"] { color: var(--success) !important; }
    hr { border-color: var(--border-color) !important; }
    .streamlit-expanderHeader {
        background: var(--bg-card) !important; border: 1px solid var(--border-color) !important;
        border-radius: 8px !important; color: var(--text-primary) !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-secondary) !important; border: 1px solid var(--border-color) !important;
        border-top: none !important; border-radius: 0 0 8px 8px !important;
    }
    .stCheckbox > label, .stRadio > label { color: var(--text-secondary) !important; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    @media (max-width: 768px) {
        [data-testid="stSidebar"] { min-width: 200px !important; max-width: 200px !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONEXIÓN A SUPABASE
# ============================================================
@st.cache_resource
def get_supabase_client() -> Client:
    """Inicializa y retorna el cliente de Supabase."""
    # Opción 1: Streamlit Secrets (recomendado para producción)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        # Opción 2: Variables de entorno (para desarrollo local)
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        st.error("""
        ⚠️ **Credenciales de Supabase no encontradas.**

        Configura tus credenciales de una de estas formas:

        **Opción A - Streamlit Secrets (recomendado):**
        Crea el archivo `.streamlit/secrets.toml` con:
        ```toml
        SUPABASE_URL = "https://tu-proyecto.supabase.co"
        SUPABASE_KEY = "tu-anon-key"
        ```

        **Opción B - Variables de entorno:**
        ```bash
        export SUPABASE_URL="https://tu-proyecto.supabase.co"
        export SUPABASE_KEY="tu-anon-key"
        ```
        """)
        st.stop()

    return create_client(url, key)

# Intentar conectar
try:
    supabase = get_supabase_client()
    connection_ok = True
except Exception as e:
    supabase = None
    connection_ok = False
    st.error(f"Error conectando a Supabase: {e}")

# ============================================================
# FUNCIONES CRUD CON SUPABASE
# ============================================================

def get_requests():
    """Obtiene todas las solicitudes de Supabase."""
    if not connection_ok:
        return []
    try:
        response = supabase.table("requests").select("*").order("created_at", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching requests: {e}")
        return []

def save_request_supabase(date_val, time_val, room, operator, req_type, notes):
    """Guarda una nueva solicitud en Supabase."""
    if not connection_ok:
        return False
    try:
        data = {
            "date": date_val.strftime("%m/%d/%Y"),
            "time": time_val.strftime("%I:%M %p"),
            "room": room.strip(),
            "operator": operator,
            "request_type": req_type,
            "notes": notes if notes else "—",
            "status": "Open",
        }
        response = supabase.table("requests").insert(data).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"Error saving request: {e}")
        return False

def delete_request_supabase(req_id):
    """Elimina una solicitud de Supabase."""
    if not connection_ok:
        return False
    try:
        supabase.table("requests").delete().eq("id", req_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting request: {e}")
        return False

def update_request_status_supabase(req_id, new_status):
    """Actualiza el status de una solicitud."""
    if not connection_ok:
        return False
    try:
        supabase.table("requests").update({"status": new_status}).eq("id", req_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating request: {e}")
        return False

def clear_all_requests_supabase():
    """Elimina todas las solicitudes (usar con cuidado)."""
    if not connection_ok:
        return False
    try:
        supabase.table("requests").delete().neq("id", 0).execute()
        return True
    except Exception as e:
        st.error(f"Error clearing requests: {e}")
        return False

# ============================================================
# OPERADORES Y TIPOS DE SOLICITUD (desde Supabase o defaults)
# ============================================================

def get_operators():
    """Obtiene operadores de Supabase o usa defaults."""
    if not connection_ok:
        return ["Fred Wayne", "Maria Garcia", "John Smith", "Sarah Chen"]
    try:
        response = supabase.table("operators").select("name").order("name").execute()
        if response.data:
            return [row["name"] for row in response.data]
    except Exception:
        pass
    return ["Fred Wayne", "Maria Garcia", "John Smith", "Sarah Chen"]

def get_request_types():
    """Obtiene tipos de solicitud de Supabase o usa defaults."""
    if not connection_ok:
        return [
            "Housekeeping", "Maintenance", "Room Service", "Concierge",
            "Transportation", "Spa & Wellness", "Restaurant Reservation",
            "Laundry", "Wake-up Call", "Complaint", "Other"
        ]
    try:
        response = supabase.table("request_types").select("name").order("name").execute()
        if response.data:
            return [row["name"] for row in response.data]
    except Exception:
        pass
    return [
        "Housekeeping", "Maintenance", "Room Service", "Concierge",
        "Transportation", "Spa & Wellness", "Restaurant Reservation",
        "Laundry", "Wake-up Call", "Complaint", "Other"
    ]

def add_operator_supabase(name):
    """Agrega un operador a Supabase."""
    if not connection_ok:
        return False
    try:
        supabase.table("operators").insert({"name": name.strip()}).execute()
        return True
    except Exception as e:
        st.error(f"Error adding operator: {e}")
        return False

def delete_operator_supabase(name):
    """Elimina un operador de Supabase."""
    if not connection_ok:
        return False
    try:
        supabase.table("operators").delete().eq("name", name).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting operator: {e}")
        return False

def add_request_type_supabase(name):
    """Agrega un tipo de solicitud a Supabase."""
    if not connection_ok:
        return False
    try:
        supabase.table("request_types").insert({"name": name.strip()}).execute()
        return True
    except Exception as e:
        st.error(f"Error adding request type: {e}")
        return False

def delete_request_type_supabase(name):
    """Elimina un tipo de solicitud de Supabase."""
    if not connection_ok:
        return False
    try:
        supabase.table("request_types").delete().eq("name", name).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting request type: {e}")
        return False

# ============================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "new_log"

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def set_page(page_name):
    st.session_state.page = page_name
    st.rerun()

def get_stats(requests_list):
    df = pd.DataFrame(requests_list)
    if df.empty:
        return {"total": 0, "today": 0, "by_type": pd.DataFrame(), "by_operator": pd.DataFrame()}

    today_str = datetime.now().strftime("%m/%d/%Y")
    total = len(df)
    today_count = len(df[df["date"] == today_str])
    by_type = df["request_type"].value_counts().reset_index()
    by_type.columns = ["Request Type", "Count"]
    by_operator = df["operator"].value_counts().reset_index()
    by_operator.columns = ["Operator", "Count"]

    return {"total": total, "today": today_count, "by_type": by_type, "by_operator": by_operator}

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:2rem; padding:0.5rem 0;">
        <div style="width:40px; height:40px; background:var(--accent); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.3rem;">📞</div>
        <div>
            <div style="font-size:1.15rem; font-weight:700; color:var(--text-primary); line-height:1.2;">Hotel Logbook</div>
            <div style="font-size:0.8rem; color:var(--text-muted);">Operators</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:1rem 0; border-color:var(--border-color);'>", unsafe_allow_html=True)

    nav_items = [
        ("new_log", "➕", "New Log"),
        ("view_logs", "📋", "View Logs"),
        ("stats", "📊", "Stats"),
        ("admin", "⚙️", "Admin"),
    ]

    for key, icon, label in nav_items:
        btn_type = "primary" if st.session_state.page == key else "secondary"
        if st.button(f"{icon}  {label}", key=f"nav_{key}", type=btn_type, use_container_width=True):
            set_page(key)

    # Estado de conexión
    if connection_ok:
        st.markdown("""
        <div style="margin-top:1rem; padding:0.5rem; background:rgba(46,213,115,0.1); border:1px solid rgba(46,213,115,0.3); border-radius:8px; text-align:center;">
            <span style="color:#2ed573; font-size:0.8rem; font-weight:600;">🟢 Connected to Supabase</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="margin-top:1rem; padding:0.5rem; background:rgba(255,71,87,0.1); border:1px solid rgba(255,71,87,0.3); border-radius:8px; text-align:center;">
            <span style="color:#ff4757; font-size:0.8rem; font-weight:600;">🔴 Supabase Disconnected</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="position:fixed; bottom:20px; left:20px; right:20px;">
        <hr style="border-color:var(--border-color); margin-bottom:0.8rem;">
        <div style="font-size:0.75rem; color:var(--text-muted); text-align:center;">
            Made by <span style="color:var(--accent);">Fred Wayne</span><br>Concierge
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PÁGINA: NEW LOG
# ============================================================
if st.session_state.page == "new_log":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
        <div style="width:28px; height:28px; background:var(--accent); border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">+</div>
        <h1 style="margin:0; font-size:1.6rem;">New Request</h1>
    </div>
    <p style="color:var(--text-muted); margin-bottom:1.5rem; font-size:0.95rem;">Log a new guest request</p>
    """, unsafe_allow_html=True)

    operators = get_operators()
    request_types = get_request_types()

    with st.container():
        st.markdown("<div style='background:#151c24; border:1px solid #1e2a38; border-radius:12px; padding:1.5rem 2rem;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='margin-bottom:1.2rem; font-size:1.1rem;'>Request Details</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("Date", value=datetime.now().date(), key="req_date")
        with col2:
            time_val = st.time_input("Time", value=datetime.now().time(), key="req_time")

        col3, col4 = st.columns(2)
        with col3:
            room = st.text_input("Room #", placeholder="e.g. 538", key="req_room")
        with col4:
            operator = st.selectbox("Operator", options=operators, index=0, key="req_operator")

        req_type = st.selectbox("Request Type", options=request_types, key="req_type")
        notes = st.text_area("Notes (optional)", placeholder="Additional details...", height=100, key="req_notes")

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

        if st.button("Save Request", type="primary", use_container_width=True):
            if not room.strip():
                st.error("⚠️ Please enter a room number.")
            else:
                success = save_request_supabase(date_val, time_val, room.strip(), operator, req_type, notes)
                if success:
                    st.success("✅ Request saved successfully to Supabase!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save request. Check your Supabase connection.")

        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PÁGINA: VIEW LOGS
# ============================================================
elif st.session_state.page == "view_logs":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
        <div style="width:28px; height:28px; background:var(--accent); border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">📋</div>
        <h1 style="margin:0; font-size:1.6rem;">View Logs</h1>
    </div>
    <p style="color:var(--text-muted); margin-bottom:1.5rem; font-size:0.95rem;">Review all logged guest requests</p>
    """, unsafe_allow_html=True)

    requests_list = get_requests()
    operators = get_operators()
    request_types = get_request_types()

    # Filtros
    with st.container():
        st.markdown("<div style='background:#151c24; border:1px solid #1e2a38; border-radius:12px; padding:1rem 1.5rem; margin-bottom:1rem;'>", unsafe_allow_html=True)

        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            filter_type = st.selectbox("Filter by Type", ["All"] + request_types, key="filter_type")
        with fcol2:
            filter_operator = st.selectbox("Filter by Operator", ["All"] + operators, key="filter_operator")
        with fcol3:
            filter_room = st.text_input("Search Room #", placeholder="e.g. 538", key="filter_room")

        st.markdown("</div>", unsafe_allow_html=True)

    df = pd.DataFrame(requests_list)

    if not df.empty:
        if filter_type != "All":
            df = df[df["request_type"] == filter_type]
        if filter_operator != "All":
            df = df[df["operator"] == filter_operator]
        if filter_room.strip():
            df = df[df["room"].astype(str).str.contains(filter_room.strip(), case=False, na=False)]

        if not df.empty:
            display_cols = ["id", "date", "time", "room", "operator", "request_type", "notes", "status"]
            available_cols = [c for c in display_cols if c in df.columns]
            display_df = df[available_cols].copy()
            display_df.columns = [c.replace("_", " ").title() for c in available_cols]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Id": st.column_config.NumberColumn("ID", width="small"),
                    "Date": st.column_config.TextColumn("Date", width="medium"),
                    "Time": st.column_config.TextColumn("Time", width="medium"),
                    "Room": st.column_config.TextColumn("Room #", width="small"),
                    "Operator": st.column_config.TextColumn("Operator", width="medium"),
                    "Request Type": st.column_config.TextColumn("Request Type", width="medium"),
                    "Notes": st.column_config.TextColumn("Notes", width="large"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                }
            )

            st.markdown(f"<p style='color:var(--text-muted); font-size:0.85rem;'>Showing {len(display_df)} request(s)</p>", unsafe_allow_html=True)

            # Acciones
            st.markdown("<h4 style='margin-top:1.5rem;'>Actions</h4>", unsafe_allow_html=True)

            acol1, acol2, acol3 = st.columns([1, 1, 3])
            with acol1:
                del_id = st.number_input("Request ID", min_value=1, step=1, key="del_id")
            with acol2:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Delete", type="secondary"):
                    if del_id in df["id"].values:
                        if delete_request_supabase(int(del_id)):
                            st.success("✅ Request deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
                    else:
                        st.error("Request ID not found.")
            with acol3:
                new_status = st.selectbox("Update Status", ["Open", "In Progress", "Completed", "Cancelled"], key="upd_status")
                if st.button("🔄 Update Status", type="secondary"):
                    if del_id in df["id"].values:
                        if update_request_status_supabase(int(del_id), new_status):
                            st.success(f"✅ Status updated to {new_status}!")
                            st.rerun()
                        else:
                            st.error("Failed to update status.")
                    else:
                        st.error("Request ID not found.")
        else:
            st.info("No requests match your filters.")
    else:
        st.info("No requests logged yet. Go to **New Log** to add one.")

# ============================================================
# PÁGINA: STATS
# ============================================================
elif st.session_state.page == "stats":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
        <div style="width:28px; height:28px; background:var(--accent); border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">📊</div>
        <h1 style="margin:0; font-size:1.6rem;">Statistics</h1>
    </div>
    <p style="color:var(--text-muted); margin-bottom:1.5rem; font-size:0.95rem;">Overview of guest request activity</p>
    """, unsafe_allow_html=True)

    requests_list = get_requests()
    operators = get_operators()
    request_types = get_request_types()
    stats = get_stats(requests_list)

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("Total Requests", stats["total"])
    with mcol2:
        st.metric("Today's Requests", stats["today"])
    with mcol3:
        st.metric("Active Operators", len(operators))
    with mcol4:
        st.metric("Request Types", len(request_types))

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

    if stats["total"] > 0:
        ccol1, ccol2 = st.columns(2)
        with ccol1:
            st.markdown("<h4 style='margin-bottom:1rem;'>Requests by Type</h4>", unsafe_allow_html=True)
            st.bar_chart(stats["by_type"].set_index("Request Type"), use_container_width=True, color="#00d4d4")
        with ccol2:
            st.markdown("<h4 style='margin-bottom:1rem;'>Requests by Operator</h4>", unsafe_allow_html=True)
            st.bar_chart(stats["by_operator"].set_index("Operator"), use_container_width=True, color="#00d4d4")

        st.markdown("<h4 style='margin-top:1.5rem;'>Recent Activity</h4>", unsafe_allow_html=True)
        recent_df = pd.DataFrame(requests_list[:10])
        if not recent_df.empty and all(c in recent_df.columns for c in ["date", "time", "room", "operator", "request_type"]):
            recent_df = recent_df[["date", "time", "room", "operator", "request_type"]]
            recent_df.columns = ["Date", "Time", "Room", "Operator", "Type"]
            st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.info("No data available yet. Start logging requests to see statistics.")

# ============================================================
# PÁGINA: ADMIN
# ============================================================
elif st.session_state.page == "admin":
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
        <div style="width:28px; height:28px; background:var(--accent); border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">⚙️</div>
        <h1 style="margin:0; font-size:1.6rem;">Admin</h1>
    </div>
    <p style="color:var(--text-muted); margin-bottom:1.5rem; font-size:0.95rem;">Manage operators, request types and data</p>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👤 Operators", "🏷️ Request Types", "💾 Data"])

    with tab1:
        st.markdown("<h4>Manage Operators</h4>", unsafe_allow_html=True)
        operators = get_operators()

        for i, op in enumerate(operators):
            ocol1, ocol2 = st.columns([4, 1])
            with ocol1:
                st.text_input(f"Operator {i+1}", value=op, key=f"op_{i}", disabled=True)
            with ocol2:
                if st.button("🗑️", key=f"del_op_{i}"):
                    if len(operators) > 1:
                        if delete_operator_supabase(op):
                            st.success(f"Removed {op}")
                            st.rerun()
                    else:
                        st.error("Need at least one operator.")

        st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)
        new_op = st.text_input("Add New Operator", placeholder="Enter name...", key="new_op")
        if st.button("➕ Add Operator", type="primary"):
            if new_op.strip() and new_op.strip() not in operators:
                if add_operator_supabase(new_op.strip()):
                    st.success(f"Added {new_op.strip()}")
                    st.rerun()
                else:
                    st.error("Failed to add operator.")
            elif new_op.strip() in operators:
                st.warning("Operator already exists.")
            else:
                st.error("Please enter a name.")

    with tab2:
        st.markdown("<h4>Manage Request Types</h4>", unsafe_allow_html=True)
        request_types = get_request_types()

        for i, rt in enumerate(request_types):
            rcol1, rcol2 = st.columns([4, 1])
            with rcol1:
                st.text_input(f"Type {i+1}", value=rt, key=f"rt_{i}", disabled=True)
            with rcol2:
                if st.button("🗑️", key=f"del_rt_{i}"):
                    if len(request_types) > 1:
                        if delete_request_type_supabase(rt):
                            st.success(f"Removed {rt}")
                            st.rerun()
                    else:
                        st.error("Need at least one request type.")

        st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)
        new_rt = st.text_input("Add New Request Type", placeholder="Enter type...", key="new_rt")
        if st.button("➕ Add Type", type="primary"):
            if new_rt.strip() and new_rt.strip() not in request_types:
                if add_request_type_supabase(new_rt.strip()):
                    st.success(f"Added {new_rt.strip()}")
                    st.rerun()
                else:
                    st.error("Failed to add request type.")
            elif new_rt.strip() in request_types:
                st.warning("Type already exists.")
            else:
                st.error("Please enter a type.")

    with tab3:
        st.markdown("<h4>Data Management</h4>", unsafe_allow_html=True)
        requests_list = get_requests()
        st.markdown(f"<p>Total requests in Supabase: <strong style='color:var(--accent);'>{len(requests_list)}</strong></p>", unsafe_allow_html=True)

        dcol1, dcol2 = st.columns(2)
        with dcol1:
            if st.button("🗑️ Clear All Requests", type="secondary"):
                if clear_all_requests_supabase():
                    st.success("All requests cleared from Supabase.")
                    st.rerun()
                else:
                    st.error("Failed to clear requests.")

        with dcol2:
            if requests_list:
                df_export = pd.DataFrame(requests_list)
                csv = df_export.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Export to CSV",
                    data=csv,
                    file_name=f"hotel_logbook_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    type="primary"
                )
