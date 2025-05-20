import sqlite3, pathlib, json

def store_row(db: pathlib.Path, row: dict):
    with sqlite3.connect(db) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS transcripts(
            id INTEGER PRIMARY KEY,
            agent TEXT, date TEXT,
            redacted_text TEXT, accuracy REAL,
            sentiment REAL, flags TEXT
        )""")
        con.execute("""INSERT INTO transcripts(agent, date, redacted_text,
                       accuracy, sentiment, flags)
                       VALUES (?,?,?,?,?,?)""",
                    (row["agent"], row["date"], row["redacted"],
                     row["accuracy"], row["sentiment"],
                     json.dumps(row["flags"])))
