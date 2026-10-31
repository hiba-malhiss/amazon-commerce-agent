import asyncio
from pprint import pprint

from langchain_core.messages import HumanMessage

from app.agent.nodes.understand import understand_node


async def main():
    # Simulate the current AgentState
    state = {
        "messages": [
            HumanMessage(
                content="Find Samsung headphones under $100"
            )
        ],
        "parameters": {},
        "entities": {},
        "requests": [],
        "tool_results": {},
    }

    # Run Understanding
    result = await understand_node(state)

    pprint(result)


if __name__ == "__main__":
    asyncio.run(main())
