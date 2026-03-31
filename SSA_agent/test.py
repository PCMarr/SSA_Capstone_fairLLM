import sqlite3
import pandas as pd

connection = sqlite3.connect("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/concept_db/pair.db")


sources = pd.read_sql_query("""
            SELECT actor, concept, title
               FROM
               pairs
               INNER JOIN actors USING (actor_id)
               INNER JOIN concepts USING (concept_id)
               INNER JOIN sources USING (source_id)
               ORDER BY source_id
            ;""", connection)

sources.to_excel("SSA_agent/concept_db/pairs.xlsx", index=False)
print(sources)
connection.close()