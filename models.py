from sqlalchemy import text
from datetime import datetime, timezone
from db import get_engine

def upsert_ticket(t: dict):
    # Defaults
    t = {**{
        "ticket_number": None,
        "issue_date": None,
        "ticket_type": None,
        "status": None,
        "sn": None,
        "gateway_id": None,
        "rma_pdf_name": None,
        "subject": None,
        "closed_date": None,
        "source": "Manual",
    }, **t}
    t["last_seen_utc"] = datetime.now(timezone.utc).isoformat()

    sql = text("""
    INSERT INTO tickets (ticket_number, issue_date, ticket_type, status, sn, gateway_id,
                         rma_pdf_name, subject, last_seen_utc, closed_date, source)
    VALUES (:ticket_number, :issue_date, :ticket_type, :status, :sn, :gateway_id,
            :rma_pdf_name, :subject, :last_seen_utc, :closed_date, :source)
    ON CONFLICT(ticket_number, source) DO UPDATE SET
        issue_date=COALESCE(excluded.issue_date, tickets.issue_date),
        ticket_type=COALESCE(excluded.ticket_type, tickets.ticket_type),
        status=COALESCE(excluded.status, tickets.status),
        sn=COALESCE(excluded.sn, tickets.sn),
        gateway_id=COALESCE(excluded.gateway_id, tickets.gateway_id),
        rma_pdf_name=COALESCE(excluded.rma_pdf_name, tickets.rma_pdf_name),
        subject=COALESCE(excluded.subject, tickets.subject),
        last_seen_utc=excluded.last_seen_utc,
        closed_date=COALESCE(excluded.closed_date, tickets.closed_date);
    """)
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(sql, t)
