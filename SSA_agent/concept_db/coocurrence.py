# builds a coocurrence matrix from the pairs stored in the pair.db file
# PARAMETERS: -s YYYY-MM-DD start date for pairs, no pairs earlier will be included in matrix
#             -e YYY-MM-DD end date for pairs, no pairs later will be included in matrix
# OUTPUT: coocurrence.csv, labeled coocurrence matrix with actors along rows and concepts along columns, numbers correspond to number of times that actor concept pair showed up in the database 

import sqlite3
import pandas as pd
from datetime import datetime
import sys
from dateutil.relativedelta import *

# actor concept list, must match actor concept list stored in database
CONCEPT_LIST = ["space as a common resource", "governing orbital sustainability", "profit", "international cooperation", "science and innovation", "national economic gains", "societal development", "diplomatic tool"]
ACTOR_LIST = ["United States","China","Russia","France","UK","NATO", "United Nations","SpaceX"]

# checks that date strings are in the format YYYY-MM-DD, returns true if so, false otherwise
def checkDateFormat(datestr):
    format = r"%Y-%m-%d"
    try:
        datetime.strptime(datestr, format)
    except ValueError:
        return False
    
    return True

# builds the SQL query which selects all actor concept pairs from the given date range.
# output is a list of actor, concept, date pairs
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

# parses the programs parameters including -s, -e, and -h. 
# output is a dictionary containing the keys start_date and end_date as needed
def parse_parameters(param_list):
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
    # gets tomorrows date, this is defualt end date
    tomorrow = datetime.now() + relativedelta(days=1)

    # parses the parameters, receives a dictionary with start and end date if given
    dates = parse_parameters(sys.argv)

    # defaults to early start date, and end date of tomorrotw
    start_date = dates.get("start_date", "1970-01-05")
    end_date = dates.get("end_date", tomorrow.strftime(r"%Y-%m-%d"))

    # gathers 
    pairs = sql_query(start_date, end_date)
    
    cooccurrnence = [[0] * len(CONCEPT_LIST) for _ in range(len(ACTOR_LIST))]

    for row in pairs.itertuples():
        try:
            cooccurrnence[ACTOR_LIST.index(row.actor)][CONCEPT_LIST.index(row.concept)] += 1
        except ValueError as e:
            print(e)

    df = pd.DataFrame(cooccurrnence)
    df.columns = CONCEPT_LIST
    df.index = ACTOR_LIST

    df.to_csv('SSA_agent/concept_db/cooccurrence.csv')



if __name__ == "__main__":
    main()