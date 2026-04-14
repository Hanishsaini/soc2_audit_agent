# import sqlite3
# from pathlib import Path
# import json

# DB_PATH = Path("./data/audit.db")
# DB_PATH.parent.mkdir(exist_ok=True)

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS findings (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             trace_id TEXT,
#             control_id TEXT,
#             status TEXT,
#             confidence REAL,
#             rationale TEXT,
#             evidence_snippet TEXT,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)
#     conn.commit()
#     conn.close()

# def save_findings(trace_id: str, findings: list):
#     conn = sqlite3.connect(DB_PATH)
#     for f in findings:
#         conn.execute(
#             """INSERT INTO findings 
#                (trace_id, control_id, status, confidence, rationale, evidence_snippet) 
#                VALUES (?,?,?,?,?,?)""",
#             (trace_id, f["control_id"], f["status"], f["confidence"], f["rationale"], f.get("evidence_snippet", ""))
#         )
#     conn.commit()
#     conn.close()

# def get_all_findings():
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.execute("SELECT trace_id, control_id, status, confidence, rationale, evidence_snippet, created_at FROM findings ORDER BY created_at DESC")
#     rows = cur.fetchall()
#     conn.close()
#     return [
#         {
#             "trace_id": r[0],
#             "control_id": r[1],
#             "status": r[2],
#             "confidence": r[3],
#             "rationale": r[4],
#             "evidence_snippet": r[5],
#             "created_at": r[6]
#         } for r in rows
#     ]

# def get_findings_by_trace(trace_id: str):
#     conn = sqlite3.connect(DB_PATH)
#     cur = conn.execute(
#         "SELECT control_id, status, confidence, rationale, evidence_snippet FROM findings WHERE trace_id = ?",
#         (trace_id,)
#     )
#     rows = cur.fetchall()
#     conn.close()
#     return [
#         {
#             "control_id": r[0],
#             "status": r[1],
#             "confidence": r[2],
#             "rationale": r[3],
#             "evidence_snippet": r[4]
#         } for r in rows
#     ]

# init_db()

import sqlite3
from pathlib import Path
import json

DB_PATH = Path("./data/audit.db")
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trace_id TEXT,
            control_id TEXT,
            status TEXT,
            confidence REAL,
            rationale TEXT,
            recommendation TEXT,
            evidence_snippet TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_findings(trace_id: str, findings: list):
    conn = sqlite3.connect(DB_PATH)
    for f in findings:
        conn.execute(
            """INSERT INTO findings 
               (trace_id, control_id, status, confidence, rationale, recommendation, evidence_snippet) 
               VALUES (?,?,?,?,?,?,?)""",
            (
                trace_id,
                f["control_id"],
                f["status"],
                f["confidence"],
                f["rationale"],
                f.get("recommendation", ""),
                f.get("evidence_snippet", "")
            )
        )
    conn.commit()
    conn.close()

def get_all_findings():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("""
        SELECT 
            trace_id, 
            control_id, 
            status, 
            confidence, 
            rationale, 
            recommendation,
            evidence_snippet, 
            created_at 
        FROM findings 
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "trace_id": r[0],
            "control_id": r[1],
            "status": r[2],
            "confidence": r[3],
            "rationale": r[4],
            "recommendation": r[5],
            "evidence_snippet": r[6],
            "created_at": r[7]
        } for r in rows
    ]

def get_findings_by_trace(trace_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        """
        SELECT 
            control_id, 
            status, 
            confidence, 
            rationale, 
            recommendation,
            evidence_snippet 
        FROM findings 
        WHERE trace_id = ?
        """,
        (trace_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "control_id": r[0],
            "status": r[1],
            "confidence": r[2],
            "rationale": r[3],
            "recommendation": r[4],
            "evidence_snippet": r[5]
        } for r in rows
    ]

init_db()