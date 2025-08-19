import asyncio
from agent.agent import search_agent

async def main():
    await search_agent.run("What is the weather in Barcelona?", max_steps=10)

if __name__ == "__main__":
    asyncio.run(main())