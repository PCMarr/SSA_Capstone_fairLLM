import sqlite3
import pandas as pd

connection = sqlite3.connect("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/concept_db/pair.db")


pairs = pd.read_sql_query("""
            SELECT actor, concept, date
               FROM
               pairs
               INNER JOIN actors USING (actor_id)
               INNER JOIN concepts USING (concept_id)
                INNER JOIN sources USING (source_id)
            ;""", connection)

concept_list = ["space as a common resource", "governing orbital sustainability", "profit", "international cooperation", "science and innovation", "national economic gains", "societal development", "diplomatic tool"]
actor_list = ["United States","China","Russia","France","UK","NATO", "United Nations","SpaceX"]
cooccurrnence = [[0] * len(concept_list) for _ in range(len(actor_list))]

for row in pairs.itertuples():
    cooccurrnence[actor_list.index(row.actor)][concept_list.index(row.concept)] += 1

df = pd.DataFrame(cooccurrnence)
df.columns = concept_list
df.index = actor_list

df.to_csv('SSA_agent/concept_db/cooccurrence.csv')

connection.close()