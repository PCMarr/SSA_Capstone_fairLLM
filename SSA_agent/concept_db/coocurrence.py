import sqlite3
import pandas as pd
from datetime import datetime
import sys
from dateutil.relativedelta import *

def checkDateFormat(datestr):
    format = r"%Y-%m-%d"
    try:
        datetime.strptime(datestr, format)
    except ValueError:
        return False
    
    return True

def sql_query(startdate, enddate):
    database_fp = "/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/concept_db/pair.db"
    conn = sqlite3.connect(database_fp)
    query = """
                SELECT actor, concept, date
                FROM
                pairs
                INNER JOIN actors USING (actor_id)
                INNER JOIN concepts USING (concept_id)
                INNER JOIN sources USING (source_id)
                WHERE UNIXEPOCH(date) - UNIXEPOCH(?) > 0 AND
                      UNIXEPOCH(date) - UNIXEPOCH(?) < 0
                ;"""
    parameters = (startdate, enddate)
    pairs = pd.read_sql_query(query, conn, params=parameters)

    conn.close()
    return pairs

def parse_parameters(param_list):
    # no arguments
    output = dict()
    if("-s" in param_list):
        try:
            start_date = param_list[param_list.index("-s") + 1]
            if(not checkDateFormat(start_date)):
                raise ValueError("date format incorrect")
            output["start_date"] = start_date
        except:
            print("paramater use:\nconcept start date: -s YYYY-MM-DD\nconcept end date: -e YYYY-MM-DD")
            exit()
    if("-e" in param_list):
        try:
            end_date = param_list[param_list.index("-e") + 1]
            if(not checkDateFormat(end_date)):
                raise ValueError("date format incorrect")
            output["end_date"] = end_date
        except:
            print("paramater use:\nconcept start date: -s YYYY-MM-DD\nconcept end date: -e YYYY-MM-DD")
            exit()
    if("-h" in param_list):
        print("paramater use:\nconcept start date: -s YYYY-MM-DD\nconcept end date: -e YYYY-MM-DD")
        exit()
    return output
    
    


def main():
    tomorrow = datetime.now() + relativedelta(days=1)
    dates = parse_parameters(sys.argv)

    start_date = dates.get("start_date", "1970-01-05")
    end_date = dates.get("end_date", tomorrow.strftime(r"%Y-%m-%d"))

    pairs = sql_query(start_date, end_date)

    concept_list = ["space as a common resource", "governing orbital sustainability", "profit", "international cooperation", "science and innovation", "national economic gains", "societal development", "diplomatic tool"]
    actor_list = ["United States","China","Russia","France","UK","NATO", "United Nations","SpaceX"]
    cooccurrnence = [[0] * len(concept_list) for _ in range(len(actor_list))]

    for row in pairs.itertuples():
        try:
            cooccurrnence[actor_list.index(row.actor)][concept_list.index(row.concept)] += 1
        except ValueError as e:
            print(e)

    df = pd.DataFrame(cooccurrnence)
    df.columns = concept_list
    df.index = actor_list

    df.to_csv('SSA_agent/concept_db/cooccurrence.csv')



if __name__ == "__main__":
    main()