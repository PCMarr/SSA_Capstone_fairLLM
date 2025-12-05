from fairlib.core.interfaces.tools import AbstractTool
import json

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
        Takes actor concept tuple, adds it to a growing JSON file
        """
        concept_list = ["space as a common resource", "governing orbital sustainability", "profit", "international cooperation", "science and innovation", "national economic gains", "societal development", "diplomatic tool"]
        pair = expression[1:]
        pair = pair[:-1]
        pair = pair.split(", ")

        if(pair[1] not in concept_list):
            raise Exception(f"{pair[1]} is not one of the accepted concepts")
        
        with open("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/actor_concept.json", "r") as file:
            json_str = file.read()
            json_obj = json.loads(json_str)

        # adds actor if not already in database
        if(json_obj.get(pair[0]) is None):
            json_obj[pair[0]] = dict()
        
        # adds concept if not already in database
        if(json_obj[pair[0]].get(pair[1]) is None):
            json_obj[pair[0]][pair[1]] = 1
        else:
            json_obj[pair[0]][pair[1]] += 1

        with open("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/actor_concept.json", "w") as file:
            json_str = json.dumps(json_obj)
            file.write(json_str)
        return(f"Successfully stored ({pair[0]}, {pair[1]})")
    
if __name__ == "__main__":
    tool = PairStorageTool()

    tool.use("(nasa, space as a common resource)")
    tool.use("(china, space as a common resource)")
    print(tool.use("(china, governing orbital sustainability)"))
