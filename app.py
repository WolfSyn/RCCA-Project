import pandas as pd
import streamlit as st
from sqlalchemy import text
from db import init_db, get_engine
from models import upsert_ticket

st.set_page_config(page_title="RCCA Ticket Tracker", layout="wide")
init_db()
eng = get_engine()

st.title("📋 RCCA / Ticket Tracker (Phase 1)")

# ---- Sidebar: Add a ticket manually ----
with st.sidebar:
    st.header("➕ Add Ticket (Manual)")
    with st.form("add_ticket"):
        ticket_number = st.text_input("Ticket Number *")
        issue_date = st.date_input("Issue Date").isoformat()
        ticket_type = st.selectbox("Type", ["", "RCCA", "LIT", "DDT"])
        status = st.selectbox("Status", ["", "Open", "In Progress", "Closed"])
        sn = st.text_input("SN")
        gateway_id = st.text_input("Gateway ID")
        rma_pdf_name = st.text_input("RMA PDF Name (e.g., RMA68.pdf)")
        subject = st.text_input("Subject / Notes")
        submitted = st.form_submit_button("Add / Update")
    if submitted:
        upsert_ticket({
            "ticket_number": ticket_number or None,
            "issue_date": issue_date or None,
            "ticket_type": ticket_type or None,
            "status": status or None,
            "sn": sn or None,
            "gateway_id": gateway_id or None,
            "rma_pdf_name": rma_pdf_name or None,
            "subject": subject or None,
            "source": "Manual"
        })
        st.success(f"Saved ticket {ticket_number}")

    st.markdown("---")
    st.header("⬆️ Import CSV (Optional)")
    st.caption("Columns recognized: ticket_number, issue_date, ticket_type, status, sn, gateway_id, rma_pdf_name, subject")
    csv = st.file_uploader("Upload CSV", type=["csv"])
    if csv is not None:
        df_up = pd.read_csv(csv)
        count = 0
        for _, r in df_up.iterrows():
            upsert_ticket({
                "ticket_number": r.get("ticket_number"),
                "issue_date": r.get("issue_date"),
                "ticket_type": r.get("ticket_type"),
                "status": r.get("status"),
                "sn": r.get("sn"),
                "gateway_id": r.get("gateway_id"),
                "rma_pdf_name": r.get("rma_pdf_name"),
                "subject": r.get("subject"),
                "source": "Manual"
            })
            count += 1
        st.success(f"Imported {count} rows")

# ---- Main: Filters + Table ----
df = pd.read_sql_query("SELECT * FROM tickets", eng)

col1, col2, col3 = st.columns([2,2,3], vertical_alignment="bottom")
with col1:
    status = st.multiselect("Status", sorted([x for x in df["status"].dropna().unique()]))
with col2:
    ttype = st.multiselect("Type", sorted([x for x in df["ticket_type"].dropna().unique()]))
with col3:
    query = st.text_input("Search (ticket/SN/Gateway/RMA/Subject)")

f = df.copy()
if status:
    f = f[f["status"].isin(status)]
if ttype:
    f = f[f["ticket_type"].isin(ttype)]
if query:
    q = query.lower()
    f = f[f.apply(lambda r: any(
        q in str(r[c]).lower()
        for c in ["ticket_number", "sn", "gateway_id", "rma_pdf_name", "subject"]
    ), axis=1)]

cols = ["ticket_number","issue_date","ticket_type","status","sn","gateway_id","rma_pdf_name","subject","source","last_seen_utc"]
cols = [c for c in cols if c in f.columns]
st.dataframe(f.sort_values(["issue_date","last_seen_utc"], ascending=[False,False])[cols],
             use_container_width=True, height=520)

st.download_button("Export CSV", f[cols].to_csv(index=False).encode("utf-8"),
                   file_name="tickets_export.csv", mime="text/csv")
