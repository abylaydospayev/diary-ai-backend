# export_json.py
import sqlite3, json

conn = sqlite3.connect("journal.db")
cur = conn.cursor()

entries = cur.execute("SELECT * FROM journal_entries").fetchall()
with open("backup.json", "w") as f:
    json.dump(entries, f, indent=2)
