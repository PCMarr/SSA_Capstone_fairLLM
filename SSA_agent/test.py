import sqlite3
import pandas as pd

connection = sqlite3.connect(r"C:\Users\Griffin.Greenwood\OneDrive - afacademy.af.edu\Documents\Capstone\SSA_Capstone_fairLLM\SSA_agent\concept_db\pair.db")


sources = pd.read_sql_query("""
            SELECT * FROM sources
            ;""", connection)

print(sources)
connection.close()