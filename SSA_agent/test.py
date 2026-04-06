import sqlite3
import pandas as pd

connection = sqlite3.connect("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/concept_db/pair.db")


sources = pd.read_sql_query("""
            SELECT date FROM sources
            ;""", connection)

print(sources)
connection.close()