import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client, Client
import os

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="Hotel Logbook",
    page_icon="📞",
    layout="wide"
)

# ============================================================
# ZONA HORARIA
# ============================================================
def get_timezone():
    try:
        return st.secrets.get("TIMEZONE", "America/Costa_Rica")
    except Exception:
        return "America/Costa_Rica"

TIMEZONE = get_timezone()

def get_local_now():
    return datetime.now(ZoneInfo(TIMEZONE))

# ============================================================
# FECHA EN ESPAÑOL
# ============================================================
MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

def fecha_español(dt):
    return f"{MESES_ES[dt.month - 1]} {dt.day}, {dt.year}"

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
.stApp { background-color: #0b0f14; }

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-testid="stSelectbox"] > div > div > div {
    background-color: #1a2330 !important;
    border: 1px solid #1e2a38 !important;
    border-radius: 8px !important;
    color: #e8ecf1 !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #5a6b7d !important; }

/* Botones */
.stButton > button[kind="primary"] {
    background: #00d4d4 !important; color: #000000 !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; width: 100% !important;
}
.stButton > button[kind="secondary"] {
    background: #1a2330 !important; color: #e8ecf1 !important;
    border: 1px solid #1e2a38 !important; border-radius: 8px !important;
}

/* Tabla */
[data-testid="stDataFrame"] th { background: #111820 !important; color: #e8ecf1 !important; }
[data-testid="stDataFrame"] td { color: #8b9aae !important; }
[data-testid="stMetricValue"] { color: #00d4d4 !important; }

/* Ocultar menú */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SUPABASE
# ============================================================
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("Configura SUPABASE_URL y SUPABASE_KEY en .streamlit/secrets.toml")
        st.stop()
    return create_client(url, key)

try:
    supabase = get_supabase_client()
    connection_ok = True
except Exception as e:
    supabase = None
    connection_ok = False
    st.error(f"Supabase error: {e}")

# ============================================================
# CRUD
# ============================================================
def get_requests():
    if not connection_ok: return []
    try:
        r = supabase.table("requests").select("*").order("created_at", desc=True).execute()
        return r.data or []
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return []

def save_request(date_val, time_val, room, operator, req_type, notes):
    if not connection_ok: return False
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
        r = supabase.table("requests").insert(data).execute()
        return bool(r.data)
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

def delete_request(req_id):
    if not connection_ok: return False
    try:
        supabase.table("requests").delete().eq("id", req_id).execute()
        return True
    except Exception as e:
        st.error(f"Delete error: {e}")
        return False

def update_status(req_id, new_status):
    if not connection_ok: return False
    try:
        supabase.table("requests").update({"status": new_status}).eq("id", req_id).execute()
        return True
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

def clear_all():
    if not connection_ok: return False
    try:
        supabase.table("requests").delete().neq("id", 0).execute()
        return True
    except Exception as e:
        st.error(f"Clear error: {e}")
        return False

def get_operators():
    if not connection_ok:
        return ["Fred Wayne", "Maria Garcia", "John Smith", "Sarah Chen"]
    try:
        r = supabase.table("operators").select("name").order("name").execute()
        if r.data: return [row["name"] for row in r.data]
    except Exception: pass
    return ["Fred Wayne", "Maria Garcia", "John Smith", "Sarah Chen"]

def get_request_types():
    if not connection_ok:
        return ["Housekeeping","Maintenance","Room Service","Concierge",
                "Transportation","Spa & Wellness","Restaurant Reservation",
                "Laundry","Wake-up Call","Complaint","Other"]
    try:
        r = supabase.table("request_types").select("name").order("name").execute()
        if r.data: return [row["name"] for row in r.data]
    except Exception: pass
    return ["Housekeeping","Maintenance","Room Service","Concierge",
            "Transportation","Spa & Wellness","Restaurant Reservation",
            "Laundry","Wake-up Call","Complaint","Other"]

def add_operator(name):
    if not connection_ok: return False
    try:
        supabase.table("operators").insert({"name": name.strip()}).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def del_operator(name):
    if not connection_ok: return False
    try:
        supabase.table("operators").delete().eq("name", name).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def add_req_type(name):
    if not connection_ok: return False
    try:
        supabase.table("request_types").insert({"name": name.strip()}).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def del_req_type(name):
    if not connection_ok: return False
    try:
        supabase.table("request_types").delete().eq("name", name).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# ============================================================
# SESSION STATE & NAV
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "new_log"

def nav_to(page):
    st.session_state.page = page
    st.rerun()

def get_stats(data):
    df = pd.DataFrame(data)
    if df.empty:
        return {"total":0,"today":0,"by_type":pd.DataFrame(),"by_operator":pd.DataFrame()}
    today = get_local_now().strftime("%m/%d/%Y")
    total = len(df)
    today_c = len(df[df["date"]==today])
    bt = df["request_type"].value_counts().reset_index()
    bt.columns = ["Request Type","Count"]
    bo = df["operator"].value_counts().reset_index()
    bo.columns = ["Operator","Count"]
    return {"total":total,"today":today_c,"by_type":bt,"by_operator":bo}

# ============================================================
# LAYOUT
# ============================================================
sidebar_col, main_col = st.columns([0.55, 4])

# ---------- SIDEBAR ----------
with sidebar_col:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:1.2rem; margin-top:0.5rem;">
        <div style="width:32px; height:32px; background:#00d4d4; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:1.1rem;">
            📞
        </div>
        <div>
            <div style="font-size:1rem; font-weight:700; color:#e8ecf1; line-height:1.2;">Hotel Logbook</div>
            <div style="font-size:0.7rem; color:#5a6b7d;">Operators</div>
        </div>
    </div>
    <hr style="border-color:#1e2a38; margin:0.8rem 0;">
    """, unsafe_allow_html=True)

    pages = [
        ("new_log", "➕", "New Log"),
        ("view_logs", "📋", "View Logs"),
        ("stats", "📊", "Stats"),
        ("admin", "⚙️", "Admin"),
    ]

    for pid, icon, label in pages:
        btn_type = "primary" if st.session_state.page == pid else "secondary"
        if st.button(f"{icon}  {label}", key=f"nav_{pid}", type=btn_type, use_container_width=True):
            nav_to(pid)

    if connection_ok:
        st.markdown("""
        <div style="margin-top:0.8rem; padding:0.35rem; background:rgba(46,213,115,0.1); border:1px solid rgba(46,213,115,0.3); border-radius:6px; text-align:center;">
            <span style="color:#2ed573; font-size:0.7rem; font-weight:600;">🟢 Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="margin-top:0.8rem; padding:0.35rem; background:rgba(255,71,87,0.1); border:1px solid rgba(255,71,87,0.3); border-radius:6px; text-align:center;">
            <span style="color:#ff4757; font-size:0.7rem; font-weight:600;">🔴 Disconnected</span>
        </div>
        """, unsafe_allow_html=True)

    # Footer + Logo
    st.markdown("""
    <div style="margin-top:2rem;">
        <hr style="border-color:#1e2a38; margin-bottom:0.5rem;">
        <div style="font-size:0.65rem; text-align:center; line-height:1.5;">
            <span style="color:#00d4d4; font-weight:700;">Made by Fred Wayne</span><br>
            <span style="color:#00d4d4; font-weight:500;">Concierge</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Logo debajo del footer
    try:
        st.image("LogoWayne.png", width=80, use_container_width=False)
    except Exception:
        st.caption("LogoWayne.png not found", help="Place LogoWayne.png in the same folder as this script")

# ============================================================
# CONTENIDO PRINCIPAL
# ============================================================
with main_col:

    # Fecha en español, alineada a la derecha, color cyan
    fecha_hoy = fecha_español(get_local_now())
    st.markdown(f"""
    <div style="text-align:right; margin-bottom:0.5rem;">
        <span style="color:#00d4d4; font-weight:700; font-size:0.95rem;">{fecha_hoy}</span>
    </div>
    """, unsafe_allow_html=True)

    # ==================== NEW LOG ====================
    if st.session_state.page == "new_log":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
            <div style="width:28px; height:28px; background:#00d4d4; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">+</div>
            <h1 style="margin:0; font-size:1.5rem; color:#e8ecf1;">New Request</h1>
        </div>
        <p style="color:#5a6b7d; margin-bottom:1.2rem; font-size:0.9rem;">Log a new guest request</p>
        """, unsafe_allow_html=True)

        operators = get_operators()
        request_types = get_request_types()

        now_local = get_local_now()
        current_date = now_local.date()
        current_time = now_local.time()
        time_str = now_local.strftime("%I:%M %p")

        st.markdown("""
        <div style="background:#151c24; border:1px solid #1e2a38; border-radius:12px; padding:1.5rem 2rem;">
            <h3 style="margin:0 0 1.2rem 0; font-size:1rem; color:#e8ecf1;">Request Details</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:0.8rem;">
            <span style="color:#5a6b7d; font-size:0.85rem;">⏰ Current local time:</span>
            <span style="color:#00d4d4; font-weight:700; font-size:0.9rem;">{time_str}</span>
            <span style="color:#5a6b7d; font-size:0.75rem;">(auto-updates on Save)</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            d = st.date_input("Date", value=current_date, key="d1")
        with c2:
            t = st.time_input("Time", value=current_time, key="t1")

        c3, c4 = st.columns(2)
        with c3:
            room = st.text_input("Room #", placeholder="e.g. 538", key="r1")
        with c4:
            op = st.selectbox("Operator", options=operators, key="o1")

        rt = st.selectbox("Request Type", options=request_types, key="rt1")
        notes = st.text_area("Notes (optional)", placeholder="Additional details...", height=100, key="n1")

        if st.button("Save Request", type="primary", use_container_width=True, key="save1"):
            if not room.strip():
                st.error("⚠️ Please enter a room number.")
            else:
                save_now = get_local_now()
                if save_request(save_now.date(), save_now.time(), room.strip(), op, rt, notes):
                    st.success("✅ Saved!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save.")

    # ==================== VIEW LOGS ====================
    elif st.session_state.page == "view_logs":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
            <div style="width:28px; height:28px; background:#00d4d4; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">📋</div>
            <h1 style="margin:0; font-size:1.5rem; color:#e8ecf1;">View Logs</h1>
        </div>
        <p style="color:#5a6b7d; margin-bottom:1.2rem; font-size:0.9rem;">Review all logged guest requests</p>
        """, unsafe_allow_html=True)

        reqs = get_requests()
        operators = get_operators()
        request_types = get_request_types()

        st.markdown("""
        <div style="background:#151c24; border:1px solid #1e2a38; border-radius:12px; padding:1rem 1.5rem; margin-bottom:1rem;">
        """, unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1:
            ft = st.selectbox("Filter by Type", ["All"] + request_types, key="ft1")
        with f2:
            fo = st.selectbox("Filter by Operator", ["All"] + operators, key="fo1")
        with f3:
            fr = st.text_input("Search Room #", placeholder="e.g. 538", key="fr1")
        st.markdown("</div>", unsafe_allow_html=True)

        df = pd.DataFrame(reqs)
        if not df.empty:
            if ft != "All":
                df = df[df["request_type"] == ft]
            if fo != "All":
                df = df[df["operator"] == fo]
            if fr.strip():
                df = df[df["room"].astype(str).str.contains(fr.strip(), case=False, na=False)]

            if not df.empty:
                cols = ["id","date","time","room","operator","request_type","notes","status"]
                avail = [c for c in cols if c in df.columns]
                disp = df[avail].copy()
                disp.columns = [c.replace("_"," ").title() for c in avail]
                st.dataframe(disp, use_container_width=True, hide_index=True)
                st.caption(f"Showing {len(disp)} request(s)")

                st.markdown("<h4 style='color:#e8ecf1; margin-top:1.2rem;'>Actions</h4>", unsafe_allow_html=True)
                a1, a2, a3 = st.columns([1,1,3])
                with a1:
                    del_id = st.number_input("Request ID", min_value=1, step=1, key="del1")
                with a2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Delete", type="secondary", key="bdel1"):
                        if del_id in df["id"].values:
                            if delete_request(int(del_id)):
                                st.success("✅ Deleted!")
                                st.rerun()
                        else:
                            st.error("ID not found.")
                with a3:
                    ns = st.selectbox("Update Status", ["Open","In Progress","Completed","Cancelled"], key="ns1")
                    if st.button("🔄 Update", type="secondary", key="bupd1"):
                        if del_id in df["id"].values:
                            if update_status(int(del_id), ns):
                                st.success(f"✅ Updated to {ns}!")
                                st.rerun()
                        else:
                            st.error("ID not found.")
            else:
                st.info("No requests match your filters.")
        else:
            st.info("No requests logged yet.")

    # ==================== STATS ====================
    elif st.session_state.page == "stats":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
            <div style="width:28px; height:28px; background:#00d4d4; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">📊</div>
            <h1 style="margin:0; font-size:1.5rem; color:#e8ecf1;">Statistics</h1>
        </div>
        <p style="color:#5a6b7d; margin-bottom:1.2rem; font-size:0.9rem;">Overview of guest request activity</p>
        """, unsafe_allow_html=True)

        reqs = get_requests()
        operators = get_operators()
        request_types = get_request_types()
        stats = get_stats(reqs)

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Requests", stats["total"])
        with m2: st.metric("Today's Requests", stats["today"])
        with m3: st.metric("Active Operators", len(operators))
        with m4: st.metric("Request Types", len(request_types))

        st.markdown("<hr style='border-color:#1e2a38; margin:1.2rem 0;'>", unsafe_allow_html=True)

        if stats["total"] > 0:
            g1, g2 = st.columns(2)
            with g1:
                st.markdown("<h4 style='color:#e8ecf1;'>Requests by Type</h4>", unsafe_allow_html=True)
                st.bar_chart(stats["by_type"].set_index("Request Type"), use_container_width=True, color="#00d4d4")
            with g2:
                st.markdown("<h4 style='color:#e8ecf1;'>Requests by Operator</h4>", unsafe_allow_html=True)
                st.bar_chart(stats["by_operator"].set_index("Operator"), use_container_width=True, color="#00d4d4")

            st.markdown("<h4 style='color:#e8ecf1; margin-top:1.2rem;'>Recent Activity</h4>", unsafe_allow_html=True)
            rdf = pd.DataFrame(reqs[:10])
            if not rdf.empty and all(c in rdf.columns for c in ["date","time","room","operator","request_type"]):
                rdf = rdf[["date","time","room","operator","request_type"]]
                rdf.columns = ["Date","Time","Room","Operator","Type"]
                st.dataframe(rdf, use_container_width=True, hide_index=True)
        else:
            st.info("No data available yet.")

    # ==================== ADMIN ====================
    elif st.session_state.page == "admin":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
            <div style="width:28px; height:28px; background:#00d4d4; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">⚙️</div>
            <h1 style="margin:0; font-size:1.5rem; color:#e8ecf1;">Admin</h1>
        </div>
        <p style="color:#5a6b7d; margin-bottom:1.2rem; font-size:0.9rem;">Manage operators, request types and data</p>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["👤 Operators", "🏷️ Request Types", "💾 Data"])

        with tab1:
            st.markdown("<h4 style='color:#e8ecf1;'>Manage Operators</h4>", unsafe_allow_html=True)
            operators = get_operators()

            for i, op in enumerate(operators):
                oc1, oc2 = st.columns([4,1])
                with oc1:
                    st.text_input(f"Operator {i+1}", value=op, key=f"op_{i}", disabled=True)
                with oc2:
                    if st.button("🗑️", key=f"dop_{i}"):
                        if len(operators) > 1:
                            if del_operator(op):
                                st.success(f"Removed {op}")
                                st.rerun()
                        else:
                            st.error("Need at least one operator.")

            st.markdown("<hr style='border-color:#1e2a38; margin:1rem 0;'>", unsafe_allow_html=True)
            new_op = st.text_input("Add New Operator", placeholder="Enter name...", key="nop")
            if st.button("➕ Add Operator", type="primary", key="bop"):
                if new_op.strip() and new_op.strip() not in operators:
                    if add_operator(new_op.strip()):
                        st.success(f"Added {new_op.strip()}")
                        st.rerun()
                    else:
                        st.error("Failed to add.")
                elif new_op.strip() in operators:
                    st.warning("Already exists.")
                else:
                    st.error("Please enter a name.")

        with tab2:
            st.markdown("<h4 style='color:#e8ecf1;'>Manage Request Types</h4>", unsafe_allow_html=True)
            request_types = get_request_types()

            for i, rt in enumerate(request_types):
                rc1, rc2 = st.columns([4,1])
                with rc1:
                    st.text_input(f"Type {i+1}", value=rt, key=f"rt_{i}", disabled=True)
                with rc2:
                    if st.button("🗑️", key=f"drt_{i}"):
                        if len(request_types) > 1:
                            if del_req_type(rt):
                                st.success(f"Removed {rt}")
                                st.rerun()
                        else:
                            st.error("Need at least one type.")

            st.markdown("<hr style='border-color:#1e2a38; margin:1rem 0;'>", unsafe_allow_html=True)
            new_rt = st.text_input("Add New Request Type", placeholder="Enter type...", key="nrt")
            if st.button("➕ Add Type", type="primary", key="brt"):
                if new_rt.strip() and new_rt.strip() not in request_types:
                    if add_req_type(new_rt.strip()):
                        st.success(f"Added {new_rt.strip()}")
                        st.rerun()
                    else:
                        st.error("Failed to add.")
                elif new_rt.strip() in request_types:
                    st.warning("Already exists.")
                else:
                    st.error("Please enter a type.")

        with tab3:
            st.markdown("<h4 style='color:#e8ecf1;'>Data Management</h4>", unsafe_allow_html=True)
            reqs = get_requests()
            st.markdown(f"<p>Total requests: <strong style='color:#00d4d4;'>{len(reqs)}</strong></p>", unsafe_allow_html=True)

            dc1, dc2 = st.columns(2)
            with dc1:
                if st.button("🗑️ Clear All", type="secondary", key="bclr"):
                    if clear_all():
                        st.success("Cleared!")
                        st.rerun()
                    else:
                        st.error("Failed.")
            with dc2:
                if reqs:
                    dfe = pd.DataFrame(reqs)
                    csv = dfe.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Export CSV",
                        data=csv,
                        file_name=f"hotel_logbook_{get_local_now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        type="primary",
                        key="bexp"
                    )
