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
    #llm = HuggingFaceAdapter("google/gemma-2-27b-it", auth_token='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', quantized=False, torch_dtype=torch.float32)
    settings.api_keys.openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = OpenAIAdapter(
        api_key=settings.api_keys.openai_api_key,
        model_name="gpt-5.1-2025-11-13"
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
    planner.prompt_builder.role_definition = \
    RoleDefinition(
        "You are an advanced expert space analyst whos job it is to analyze contextual sources.\n"
        "You will read articles given to you and store the actor-concept pairings that show up in the given article.\n"
        "You will ONLY look for the following concepts:\n"
        f"{concept_list}"
        "You must find all pairings of actors and concepts that they portray from the article and use the tools given to you to store them in a database using the provided tools\n"
        "You must reason step-by-step to find all pairings. If an article contains multiple actors or concepts"
        "you must break it down and store one actor paired with one concept at a time. You will store the actor pair concepts using the pair_storage_tool."
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
    sources_json = []
    with open("SSA_agent/source_collection/sources.json", "r") as fp:
        sources_json = json.load(fp)

    
    for i in range(len(sources_json)):
        title = sources_json[i]["title"]
        print(f"\n\nNext source: {title} ")
        try:
            user_input = sources_json[i]["text"]

            # Run the agent’s full Reason+Act cycle
            agent_response = await agent.arun(user_input)
            print(f"🤖 Agent: {agent_response}")

        except KeyboardInterrupt:
            print("\n🤖 Agent: Session ended by user.")
            break
        except Exception as e:
            print(f"❌ Agent error: {e}")


# Entrypoint for script execution
if __name__ == "__main__":
    asyncio.run(main())
