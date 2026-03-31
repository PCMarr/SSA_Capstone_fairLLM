import sqlite3
import pandas as pd

connection = sqlite3.connect("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/concept_db/pair.db")


sources = pd.read_sql_query("""
            SELECT source_id, title, content FROM sources
            ;""", connection)

sources.to_excel("SSA_agent/concept_db/sources.xlsx", index=False)
print(sources)
connection.close()