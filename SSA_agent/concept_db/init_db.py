import sqlite3

# builds the database structure from a schema file
if __name__ == "__main__":
    db_file = "SSA_agent/concept_db/schema.sql"
    conn = sqlite3.connect("SSA_agent/concept_db/pair.db")
    conn.execute("PRAGMA foreign_keys = ON")

    cur = conn.cursor()
    with open(db_file, "r") as fp:
        conn.executescript(fp.read())

    conn.close()