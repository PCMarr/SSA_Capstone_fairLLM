# demo_advanced_calculator_calculus.py

"""
This script demonstrates how to assemble a single intelligent agent that can reason,
respond, and use tools in a mathematically rich environment.

The agent supports:
    1. Basic arithmetic calculations using SafeCalculatorTool
    2. Symbolic calculus operations (derivatives and integrals) using AdvancedCalculusTool

This serves as a practical tutorial for combining multiple tools under the FAIR-LLM framework.
"""

import asyncio

# --- Step 1: Import necessary framework components ---
from fairlib import (
    ToolRegistry,
    ToolExecutor,
    WorkingMemory,
    SimpleAgent,
    SafeCalculatorTool,
    RoleDefinition, 
    HuggingFaceAdapter,
    SimpleReActPlanner
)

# --- Step 2: Import the additiojnal tools we want this agent to use ---
# NOTE: SafeCalculatorTool is a built-in tool while AdvancedCalculusTool 
# is a tool we built to extend beyond our basic built-in tools.

from fairlib.modules.action.tools.ac_pair_storage_tool import PairStorageTool


async def main():
    """
    Main entry point for the demo agent.
    This sets up the brain, memory, planner, tools, and interaction loop.
    """
    print("🔧 Initializing the SSA agent...")
   
    # === (a) Brain: Language Model ===
    llm = HuggingFaceAdapter("dolphin3-qwen25-3b", auth_token='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')
    
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
    
    planner = SimpleReActPlanner(llm, tool_registry)

    # modify the default role a bit:
    planner.prompt_builder.role_definition = \
    RoleDefinition(
        "You are an advanced expert space analyst whos job it is to analyze contextual sources.\n"
        "You will read articles given to you and store the actor-concept pairings that show up in the given article.\n"
        "You will ONLY look for the following concepts: space as a common resource, governing orbital sustainability, profit, international cooperation, science and innovation, national economic gains, societal development, and diplomatic tool.\n"
        "You must find all pairings of actors and concepts that they portray from the article and use the tools given to you to store them in a database using the provided tools\n"
        "You must reason step-by-step to determine the best course of action. If an article contains multiple actors or concepts"
        "you must break it down store one actor paired with one concept at a time."
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
    while True:
        try:
            user_input = input("👤 You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("🤖 Agent: Goodbye! 👋")
                break

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
