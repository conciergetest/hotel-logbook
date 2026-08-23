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
    layout="wide"
)

# ============================================================
# CSS MÍNIMO - Solo colores, sin tocar layout
# ============================================================
st.markdown("""
<style>
.stApp {
    background-color: #0b0f14;
}
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
[data-testid="stTextArea"] textarea::placeholder {
    color: #5a6b7d !important;
}
.stButton > button[kind="primary"] {
    background: #00d4d4 !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
}
.stButton > button[kind="secondary"] {
    background: #1a2330 !important;
    color: #e8ecf1 !important;
    border: 1px solid #1e2a38 !important;
    border-radius: 8px !important;
}
[data-testid="stDataFrame"] th {
    background: #111820 !important;
    color: #e8ecf1 !important;
}
[data-testid="stDataFrame"] td {
    color: #8b9aae !important;
}
[data-testid="stMetricValue"] {
    color: #00d4d4 !important;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONEXIÓN A SUPABASE
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
# FUNCIONES CRUD
# ============================================================
def get_requests():
    if not connection_ok: return []
    try:
        response = supabase.table("requests").select("*").order("created_at", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return []

def save_request_supabase(date_val, time_val, room, operator, req_type, notes):
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
        response = supabase.table("requests").insert(data).execute()
        return True if response.data else False
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

def delete_request_supabase(req_id):
    if not connection_ok: return False
    try:
        supabase.table("requests").delete().eq("id", req_id).execute()
        return True
    except Exception as e:
        st.error(f"Delete error: {e}")
        return False

def update_request_status_supabase(req_id, new_status):
    if not connection_ok: return False
    try:
        supabase.table("requests").update({"status": new_status}).eq("id", req_id).execute()
        return True
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

def clear_all_requests_supabase():
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
        response = supabase.table("operators").select("name").order("name").execute()
        if response.data:
            return [row["name"] for row in response.data]
    except Exception:
        pass
    return ["Fred Wayne", "Maria Garcia", "John Smith", "Sarah Chen"]

def get_request_types():
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
    if not connection_ok: return False
    try:
        supabase.table("operators").insert({"name": name.strip()}).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def delete_operator_supabase(name):
    if not connection_ok: return False
    try:
        supabase.table("operators").delete().eq("name", name).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def add_request_type_supabase(name):
    if not connection_ok: return False
    try:
        supabase.table("request_types").insert({"name": name.strip()}).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def delete_request_type_supabase(name):
    if not connection_ok: return False
    try:
        supabase.table("request_types").delete().eq("name", name).execute()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# ============================================================
# SESSION STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "new_log"

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
# LAYOUT: SIDEBAR SIMULADO CON COLUMNS (más fiable en Cloud)
# ============================================================
sidebar_col, main_col = st.columns([1.2, 4])

# ---------- SIDEBAR SIMULADO ----------
with sidebar_col:
    st.markdown("""
    <div style="background:#111820; border-right:1px solid #1e2a38; padding:1rem; min-height:100vh; margin:-6rem -1rem -10rem -1rem;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:1.5rem; padding-top:1rem;">
            <div style="width:36px; height:36px; background:#00d4d4; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:1.2rem;">
                📞
            </div>
            <div>
                <div style="font-size:1.1rem; font-weight:700; color:#e8ecf1; line-height:1.2;">Hotel Logbook</div>
                <div style="font-size:0.75rem; color:#5a6b7d;">Operators</div>
            </div>
        </div>
        <hr style="border-color:#1e2a38; margin:1rem 0;">
    """, unsafe_allow_html=True)

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

    if connection_ok:
        st.markdown("""
        <div style="margin-top:1rem; padding:0.4rem; background:rgba(46,213,115,0.1); border:1px solid rgba(46,213,115,0.3); border-radius:6px; text-align:center;">
            <span style="color:#2ed573; font-size:0.75rem; font-weight:600;">🟢 Connected</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="margin-top:1rem; padding:0.4rem; background:rgba(255,71,87,0.1); border:1px solid rgba(255,71,87,0.3); border-radius:6px; text-align:center;">
            <span style="color:#ff4757; font-size:0.75rem; font-weight:600;">🔴 Disconnected</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div style="position:absolute; bottom:20px; left:20px; right:20px;">
            <hr style="border-color:#1e2a38; margin-bottom:0.6rem;">
            <div style="font-size:0.7rem; color:#5a6b7d; text-align:center;">
                Made by <span style="color:#00d4d4;">Fred Wayne</span><br>Concierge
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- CONTENIDO PRINCIPAL ----------
with main_col:
    # PÁGINA: NEW LOG
    if st.session_state.page == "new_log":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
            <div style="width:28px; height:28px; background:#00d4d4; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">+</div>
            <h1 style="margin:0; font-size:1.5rem; color:#e8ecf1;">New Request</h1>
        </div>
        <p style="color:#5a6b7d; margin-bottom:1.5rem; font-size:0.9rem;">Log a new guest request</p>
        """, unsafe_allow_html=True)

        operators = get_operators()
        request_types = get_request_types()

        st.markdown("""
        <div style="background:#151c24; border:1px solid #1e2a38; border-radius:12px; padding:1.5rem 2rem; margin-bottom:1rem;">
            <h3 style="margin:0 0 1.2rem 0; font-size:1rem; color:#e8ecf1;">Request Details</h3>
        </div>
        """, unsafe_allow_html=True)

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

        if st.button("Save Request", type="primary", use_container_width=True):
            if not room.strip():
                st.error("⚠️ Please enter a room number.")
            else:
                success = save_request_supabase(date_val, time_val, room.strip(), operator, req_type, notes)
                if success:
                    st.success("✅ Request saved!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save.")

    # PÁGINA: VIEW LOGS
    elif st.session_state.page == "view_logs":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
            <div style="width:28px; height:28px; background:#00d4d4; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">📋</div>
            <h1 style="margin:0; font-size:1.5rem; color:#e8ecf1;">View Logs</h1>
        </div>
        <p style="color:#5a6b7d; margin-bottom:1.5rem; font-size:0.9rem;">Review all logged guest requests</p>
        """, unsafe_allow_html=True)

        requests_list = get_requests()
        operators = get_operators()
        request_types = get_request_types()

        st.markdown("""
        <div style="background:#151c24; border:1px solid #1e2a38; border-radius:12px; padding:1rem 1.5rem; margin-bottom:1rem;">
        """, unsafe_allow_html=True)

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

                st.dataframe(display_df, use_container_width=True, hide_index=True)
                st.caption(f"Showing {len(display_df)} request(s)")

                st.markdown("<h4 style='color:#e8ecf1; margin-top:1.5rem;'>Actions</h4>", unsafe_allow_html=True)

                acol1, acol2, acol3 = st.columns([1, 1, 3])
                with acol1:
                    del_id = st.number_input("Request ID", min_value=1, step=1, key="del_id")
                with acol2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Delete", type="secondary"):
                        if del_id in df["id"].values:
                            if delete_request_supabase(int(del_id)):
                                st.success("✅ Deleted!")
                                st.rerun()
                        else:
                            st.error("ID not found.")
                with acol3:
                    new_status = st.selectbox("Update Status", ["Open", "In Progress", "Completed", "Cancelled"], key="upd_status")
                    if st.button("🔄 Update Status", type="secondary"):
                        if del_id in df["id"].values:
                            if update_request_status_supabase(int(del_id), new_status):
                                st.success(f"✅ Updated to {new_status}!")
                                st.rerun()
                        else:
                            st.error("ID not found.")
            else:
                st.info("No requests match your filters.")
        else:
            st.info("No requests logged yet.")

    # PÁGINA: STATS
    elif st.session_state.page == "stats":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
            <div style="width:28px; height:28px; background:#00d4d4; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">📊</div>
            <h1 style="margin:0; font-size:1.5rem; color:#e8ecf1;">Statistics</h1>
        </div>
        <p style="color:#5a6b7d; margin-bottom:1.5rem; font-size:0.9rem;">Overview of guest request activity</p>
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

        st.markdown("<hr style='border-color:#1e2a38; margin:1.5rem 0;'>", unsafe_allow_html=True)

        if stats["total"] > 0:
            ccol1, ccol2 = st.columns(2)
            with ccol1:
                st.markdown("<h4 style='color:#e8ecf1;'>Requests by Type</h4>", unsafe_allow_html=True)
                st.bar_chart(stats["by_type"].set_index("Request Type"), use_container_width=True, color="#00d4d4")
            with ccol2:
                st.markdown("<h4 style='color:#e8ecf1;'>Requests by Operator</h4>", unsafe_allow_html=True)
                st.bar_chart(stats["by_operator"].set_index("Operator"), use_container_width=True, color="#00d4d4")

            st.markdown("<h4 style='color:#e8ecf1; margin-top:1.5rem;'>Recent Activity</h4>", unsafe_allow_html=True)
            recent_df = pd.DataFrame(requests_list[:10])
            if not recent_df.empty and all(c in recent_df.columns for c in ["date", "time", "room", "operator", "request_type"]):
                recent_df = recent_df[["date", "time", "room", "operator", "request_type"]]
                recent_df.columns = ["Date", "Time", "Room", "Operator", "Type"]
                st.dataframe(recent_df, use_container_width=True, hide_index=True)
        else:
            st.info("No data available yet.")

    # PÁGINA: ADMIN
    elif st.session_state.page == "admin":
        st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:0.3rem;">
            <div style="width:28px; height:28px; background:#00d4d4; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#000; font-weight:700; font-size:1rem;">⚙️</div>
            <h1 style="margin:0; font-size:1.5rem; color:#e8ecf1;">Admin</h1>
        </div>
        <p style="color:#5a6b7d; margin-bottom:1.5rem; font-size:0.9rem;">Manage operators, request types and data</p>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["👤 Operators", "🏷️ Request Types", "💾 Data"])

        with tab1:
            st.markdown("<h4 style='color:#e8ecf1;'>Manage Operators</h4>", unsafe_allow_html=True)
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

            st.markdown("<hr style='border-color:#1e2a38; margin:1rem 0;'>", unsafe_allow_html=True)
            new_op = st.text_input("Add New Operator", placeholder="Enter name...", key="new_op")
            if st.button("➕ Add Operator", type="primary"):
                if new_op.strip() and new_op.strip() not in operators:
                    if add_operator_supabase(new_op.strip()):
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
                            st.error("Need at least one type.")

            st.markdown("<hr style='border-color:#1e2a38; margin:1rem 0;'>", unsafe_allow_html=True)
            new_rt = st.text_input("Add New Request Type", placeholder="Enter type...", key="new_rt")
            if st.button("➕ Add Type", type="primary"):
                if new_rt.strip() and new_rt.strip() not in request_types:
                    if add_request_type_supabase(new_rt.strip()):
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
            requests_list = get_requests()
            st.markdown(f"<p>Total requests: <strong style='color:#00d4d4;'>{len(requests_list)}</strong></p>", unsafe_allow_html=True)

            dcol1, dcol2 = st.columns(2)
            with dcol1:
                if st.button("🗑️ Clear All", type="secondary"):
                    if clear_all_requests_supabase():
                        st.success("Cleared!")
                        st.rerun()
                    else:
                        st.error("Failed.")

            with dcol2:
                if requests_list:
                    df_export = pd.DataFrame(requests_list)
                    csv = df_export.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Export CSV",
                        data=csv,
                        file_name=f"hotel_logbook_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        type="primary"
                    )
