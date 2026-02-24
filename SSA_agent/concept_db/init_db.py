import sqlite3

if __name__ == "__main__":
    db_file = "SSA_agent/concept_db/schema.db"
    conn = sqlite3.connect("SSA_agent/concept_db/pair.db")
    conn.execute("PRAGMA foreign_keys = ON")

    cur = conn.cursor()
    with open(db_file, "r") as fp:
        conn.executescript(fp.read())

    conn.close()