from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "./tickets.db")

_engine = None
def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    return _engine

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS tickets (
  id INTEGER PRIMARY KEY,
  ticket_number TEXT,
  issue_date TEXT,
  ticket_type TEXT,          -- RCCA | LIT | DDT
  status TEXT,               -- Open | Closed | In Progress
  sn TEXT,
  gateway_id TEXT,
  rma_pdf_name TEXT,         -- e.g., RMA68.pdf
  subject TEXT,
  last_seen_utc TEXT,
  closed_date TEXT,
  source TEXT,               -- 'Manual' for Phase 1
  UNIQUE(ticket_number, source)
);
"""

def init_db():
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text(SCHEMA_SQL))
