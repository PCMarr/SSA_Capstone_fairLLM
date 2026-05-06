import sqlite3
import pandas as pd

connection = sqlite3.connect(r"/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/concept_db/pair_test.db")


sources = pd.read_sql_query("""
            SELECT count(*) FROM sources
            ;""", connection)

print(sources)
connection.close()