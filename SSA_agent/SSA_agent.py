import torch
import json
import asyncio
from dotenv import load_dotenv
load_dotenv()
import os
import sqlite3
from translation import translate

# --- Step 1: Import necessary framework components ---
from fairlib import (
    settings,
    ToolRegistry,
    ToolExecutor,
    WorkingMemory,
    SimpleAgent,
    SafeCalculatorTool,
    RoleDefinition, 
    HuggingFaceAdapter,
    SimpleReActPlanner,
    OpenAIAdapter,
    ReActPlanner
)

# --- Step 2: Import the additional tools we want this agent to use ---

from ac_pair_storage_tool import PairStorageTool


async def main():
    """
    Main entry point for the demo agent.
    This sets up the brain, memory, planner, tools, and interaction loop.
    """
    print("🔧 Initializing the SSA agent...")
   
    # === (a) Brain: Language Model ===
    
    settings.api_keys.openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = OpenAIAdapter(
        api_key=settings.api_keys.openai_api_key,
        model_name="gpt-4.1-2025-04-14"
    )
    # === (b) Toolbelt: Register tools ===
    tool_registry = ToolRegistry()
    storage_tool = PairStorageTool()


    # Register tools with the registry
    tool_registry.register_tool(storage_tool)

    print(f"✅ Registered tools: {[tool.name for tool in tool_registry.get_all_tools().values()]}")

    # === (c) Hands: Tool Executor ===
    executor = ToolExecutor(tool_registry)

    # === (d) Memory: Conversation Context ===
    memory = WorkingMemory()

    # === (e) Mind: Reasoning Engine ===

    
    planner = ReActPlanner(llm, tool_registry)

    # agent role definition, explains what the agent is supposed to do when the sources are passed to it
    concept_list = ["space as a common resource", "governing orbital sustainability", "profit", "international cooperation", "science and innovation", "national economic gains", "societal development", "diplomatic tool"]
    actor_list = ["United States","China","Russia","France","UK","NATO", "United Nations","SpaceX"]
    planner.prompt_builder.role_definition = \
        RoleDefinition(
        "You are an advanced expert space analyst whos job it is to analyze contextual sources.\n"
       "You will be given text from an article which you will analyze to find actor-concept pairs."
       f"The actors you are analyzing are: {actor_list}\n"
       f"The concepts you can link them to are: {concept_list}\n"
       "You must find one actor-concept pair at a time, cite the part of the text where you see this pairing, and store it in the database using the pair-storage-tool\n"
       "You must read the entire article and find all actor-concept pairs from the text, but"
       "You must only store one actor-concept pair at a time, you must not attempt to store more than one at a time."
       "You will not inferred actors; only create a pair if the actor is explicitly names in the text."
       "Do not inter actors from alliances, partnerships, affiliations, or indirect references.\n"
       "You will not assume links."
       "Both the actor and the concept must be directly connected in meaning within the same context."
       "If the actor and concept are merely mentioned in the article but not clearly related to each other, do not create a pair.\n"
       "You will not include opposite links."
        "Do not create a pair if the actor is described as acting against, undermining, violating, or contradicting the concept."
       "Only create the pair if the actor is described as supporting, promoting, regulating, governing, or advancing the concept.\n"
       "You will not include historical only mentions."
        "Do not create a pair if the connection is purely historical background and not relevant to the article’s present discussion or current positioning.\n"
        "You will include positive or direct engagement pairs."
        "The actor must be actively promoting, benefiting from, regulating, advancing, funding, leveraging, or strategically using the concept."
    )

    # === (f) Assemble the Agent ===
    agent = SimpleAgent(
        llm=llm,
        planner=planner,
        tool_executor=executor,
        memory=memory,
        max_steps=10  # Limit reasoning loops to prevent runaway execution
    )

    # === (g) Interaction Loop ===
    temp_file = "temp.json"

    # gathers all sources from the database, change 
    database_fp = "/home/peter-marriott/SSA_Capstone_fairLLM/SSA_agent/concept_db/pair.db"
    connection = sqlite3.connect(database_fp)
    cursor = connection.cursor()
    cursor.execute("""
            SELECT source_id, title, content FROM sources;
            """)

    rows = cursor.fetchall()
    connection.close()

    # loops through sources, calls llm on each one in succession
    for source in rows:
        source_id = source[0]
        title = source[1]
        content = source[2]  # content of the source
        try:
            user_input = content
            if(user_input):  # only calls LLM if the source has content
                print(f"\n\nNext source: {title} ")

                # outputs the source_id to a temporary file which is read by the pair storage tool to input the correct pairs
                with open(temp_file, "w") as fp:
                    fp.write(f"{source_id}")

                # Run the agent’s full Reason+Act cycle
                agent_response = await agent.arun(user_input)

        except KeyboardInterrupt:
            os.remove(temp_file)
            print("\n🤖 Agent: Session ended by user.")
            break
        except Exception as e:
            os.remove(temp_file)
            print(f"❌ Agent error: {e}")
    os.remove(temp_file)

# Entrypoint for script execution
if __name__ == "__main__":
    asyncio.run(main())
