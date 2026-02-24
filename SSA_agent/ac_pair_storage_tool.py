from fairlib.core.interfaces.tools import AbstractTool
import sqlite3

class PairStorageTool(AbstractTool):
    name = "pair_storage_tool"
    description = (
        "A tool used for storing actor concept pairs in a database.\n"
        "Inputs will be a tuple containing the actor and concept"
        "Examples:\n"
        "(U.S. Department of Defense, diplomatic tool)\n"
        "(SpaceX, Profit)"
    )

    def use(self, expression: str) -> str:
        """
        Takes actor concept tuple, adds it to a growing database
        """
        concept_list = ["space as a common resource", "governing orbital sustainability", "profit", "international cooperation", "science and innovation", "national economic gains", "societal development", "diplomatic tool"]
        actor_list =  ["United States","China","Russia","France","UK","NATO", "United Nations","SpaceX"]
        pair = expression[1:]
        pair = pair[:-1]
        pair = pair.split(", ")
        
        if(pair[0] not in actor_list):
            raise Exception(f"{pair[0]} is not one of the accepted actors")

        if(pair[1] not in concept_list):
            raise Exception(f"{pair[1]} is not one of the accepted concepts")
        
        #put actor concept pairs into database https://docs.python.org/3/library/sqlite3.html
        connection = sqlite3.connect("SSA_agent/concept_db/pair.db")
        cursor = connection.cursor()

        cursor.execute("SELECT actor_id FROM actors WHERE actor=?", (pair[0],))
        actor_id = cursor.fetchone()[0]

        cursor.execute("SELECT concept_id FROM concepts WHERE concept=?", (pair[1],))
        concept_id = cursor.fetchone()[0]

        source_id = 1

        cursor.execute("INSERT INTO pairs (actor_id, concept_id, source_id) VALUES (?, ?, ?)",
                       (actor_id, concept_id, source_id))
        
        connection.commit()
        connection.close()


        # with open("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/actor_concept.json", "r") as file:
        #     json_str = file.read()
        #     json_obj = json.loads(json_str)

        # # adds actor if not already in database
        # if(json_obj.get(pair[0]) is None):
        #     json_obj[pair[0]] = dict()
        
        # # adds concept if not already in database
        # if(json_obj[pair[0]].get(pair[1]) is None):
        #     json_obj[pair[0]][pair[1]] = 1
        # else:
        #     json_obj[pair[0]][pair[1]] += 1

        # with open("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/actor_concept.json", "w") as file:
        #     json_str = json.dumps(json_obj)
        #     file.write(json_str)
        # return(f"Successfully stored ({pair[0]}, {pair[1]})")
    
if __name__ == "__main__":
    tool = PairStorageTool()

    connection = sqlite3.connect("SSA_agent/concept_db/pair.db")
    cursor = connection.cursor()

    cursor.execute("""
                    INSERT INTO actors (actor) VALUES
                    ("United States"),
                    ("China"),
                    ("Russia"),
                    ("France"),
                    ("UK"),
                    ("NATO"),
                    ("United Nations"),
                    ("SpaceX")
                    """)
    
    cursor.execute("""
                    INSERT INTO concepts (concept) VALUES
                    ("space as a common resource"),
                    ("governing orbital sustainability"),
                    ("profit"), 
                    ("international cooperation"),
                    ("science and innovation"),
                    ("national economic gains"),
                    ("societal development"),
                    ("diplomatic tool")
                    """)
    
    connection.commit()
    
    connection.close()

    tool.use("(Russia, space as a common resource)")
    tool.use("(China, space as a common resource)")

    connection = sqlite3.connect("SSA_agent/concept_db/pair.db")
    cursor = connection.cursor()

    cursor.execute("DELETE FROM pairs")