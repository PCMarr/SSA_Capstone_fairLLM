import sqlite3

connection = sqlite3.connect("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/concept_db/pair.db")
cursor = connection.cursor()



cursor.execute("""
            SELECT COUNT(title) FROM sources;
            """)

rows = cursor.fetchall()
print(rows)