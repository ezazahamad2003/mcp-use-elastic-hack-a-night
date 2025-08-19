"""
Simple chat example using MCPAgent with built-in conversation memory.

This example demonstrates how to use the MCPAgent with its built-in
conversation history capabilities for better contextual interactions.

Special thanks to https://github.com/microsoft/playwright-mcp for the server.
"""

import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agent.agent import search_agent
from agent.utils import Spinner
from mcp_use import set_debug

set_debug(0)

async def run_memory_chat():

    print("\n===== Interactive MCP Chat =====")
    print("Type 'exit' or 'quit' to end the conversation")
    print("Type 'clear' to clear conversation history")
    print("==================================\n")

    try:
        # Main chat loop
        while True:
            # Get user input
            user_input = input("\nYou: ")

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Ending conversation...")
                break

            # Check for clear history command
            if user_input.lower() == "clear":
                search_agent.clear_conversation_history()
                print("Conversation history cleared.")
                continue

            # Get response from agent
            print("\nAssistant: ", end="", flush=True)

            try:
                # Run the agent with the user input (memory handling is automatic)
                async with Spinner():
                    response = await search_agent.run(user_input, max_steps=10)
                print(response)

            except Exception as e:
                print(f"\nError: {e}")

    finally:
        # Clean up
        await search_agent.close()

if __name__ == "__main__":
    asyncio.run(run_memory_chat())
