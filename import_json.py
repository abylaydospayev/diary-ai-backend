# import_json.py
import sqlite3
import json

def import_json_to_db(json_file="journal_backup.json", db_file="journal.db"):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    with open(json_file, "r") as f:
        data = json.load(f)

    for entry in data:
        cursor.execute("""
            INSERT INTO journal_entries (entry, reflection, timestamp)
            VALUES (?, ?, ?)
        """, (entry["entry"], entry["reflection"], entry["timestamp"]))

    conn.commit()
    conn.close()
    print(f"✅ Imported {len(data)} entries from {json_file}")

if __name__ == "__main__":
    import_json_to_db()
