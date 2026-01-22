# demo_advanced_calculator_calculus.py

"""
This script demonstrates how to assemble a single intelligent agent that can reason,
respond, and use tools in a mathematically rich environment.

The agent supports:
    1. Basic arithmetic calculations using SafeCalculatorTool
    2. Symbolic calculus operations (derivatives and integrals) using AdvancedCalculusTool

This serves as a practical tutorial for combining multiple tools under the FAIR-LLM framework.
"""
import torch
import json
import asyncio
from dotenv import load_dotenv
load_dotenv()
import os

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

# --- Step 2: Import the additiojnal tools we want this agent to use ---
# NOTE: SafeCalculatorTool is a built-in tool while AdvancedCalculusTool 
# is a tool we built to extend beyond our basic built-in tools.

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
    # === (b) Toolbelt: Register both calculator and calculus tools ===
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
    #planner = ReActPlanner(llm, tool_registry)
        # For use with simple, local models
    
    planner = ReActPlanner(llm, tool_registry)

    # modify the default role a bit:
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
        "you must only store one actor-concept pair at a time, you must not attempt to store more than one at a time."
    )
    # RoleDefinition(
    #     "You are an advanced expert space analyst whos job it is to analyze contextual sources.\n"
    #     "You should only focus on articles relevent to the space domain, do not analyze any irrelevant articles"
    #     "You will read articles given to you and store the actor-concept pairings that show up in the given article. Provide citations from the text which support your selections\n"
    #     "Actors are defined as specific organization, political group, social group, or other organization of people invested in the space domain in some way.\n"
    #     "You will ONLY look for the following concepts:\n"
    #     f"{concept_list}"
    #     "You must find all pairings of actors and concepts that they portray from the article and use the pair_storage_tool to to store them in a database.\n"
    #     "You must reason step-by-step to find all pairings. If an article contains multiple actors or concepts"
    #     "you must break it down and store one actor paired with one concept at a time, the pair_storage_tool can only accept one actor concept pair at a time."
    # )

    # === (f) Assemble the Agent ===
    agent = SimpleAgent(
        llm=llm,
        planner=planner,
        tool_executor=executor,
        memory=memory,
        max_steps=10  # Limit reasoning loops to prevent runaway execution
    )


    # === (g) Interaction Loop ===
    sources_json = []
    with open("SSA_agent/source_collection/sources.json", "r") as fp:
        sources_json = json.load(fp)

    num_sources = len(sources_json)
    for i in range(num_sources):
        title = sources_json[i]["title"]
        try:
            user_input = sources_json[i]["text"]
            if(user_input):
                print(f"\n\n({i}/{num_sources}) Next source: {title} ")
                # Run the agent’s full Reason+Act cycle
                agent_response = await agent.arun(user_input)
                # print(f"🤖 Agent: {agent_response}")

        except KeyboardInterrupt:
            print("\n🤖 Agent: Session ended by user.")
            break
        except Exception as e:
            print(f"❌ Agent error: {e}")


# Entrypoint for script execution
if __name__ == "__main__":
    asyncio.run(main())
