import json
with open("/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/actor_concept.json", "r") as fp:
    data = json.load(fp)

print(len(data))