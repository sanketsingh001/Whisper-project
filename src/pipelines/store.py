import sqlite3, pathlib, json

_TABLE = "transcript_v2"          # ← new table name in one place

def _init_schema(con: sqlite3.Connection):
    con.execute(f"""
    CREATE TABLE IF NOT EXISTS {_TABLE}(
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        agent           TEXT,
        date            TEXT,
        redacted_text   TEXT,
        accuracy        REAL,
        conf            REAL,
        sentiment       REAL,
        coverage        REAL,
        coverage_detail TEXT,
        flags           TEXT
    )
    """)
    # You can add more columns later; just extend both CREATE + INSERT.

def store_row(db: pathlib.Path, row: dict):
    with sqlite3.connect(db) as con:
        _init_schema(con)
        con.execute(f"""
        INSERT INTO {_TABLE}(
            agent, date, redacted_text,
            accuracy, conf, sentiment,
            coverage, coverage_detail,
            flags)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            row.get("agent"),
            row.get("date"),
            row.get("redacted"),
            row.get("accuracy"),
            row.get("conf"),
            row.get("sentiment"),
            row.get("coverage"),
            json.dumps(row.get("coverage_detail")),
            json.dumps(row.get("flags", []))
        ))
