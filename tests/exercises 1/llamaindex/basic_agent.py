import asyncio
import os
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai_like import OpenAILike
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec


class LlamaIndexAgent:
    MODEL = 'qwen3:32b'
    API_KEY = os.getenv("VISTEON_OLLAMA_TOKEN")

    def __init__(self):
        self._agent = None
        self._ctx = None

    async def setup(self):
        llm = OpenAILike(
            model=self.MODEL, api_base='http://chipd120.vistcorp.ad.visteon.com:8000/v1', api_key=self.API_KEY, timeout=600,
            is_chat_model=True, is_function_calling_model=True
        )
        mcp_client = BasicMCPClient(
            '.venv\\Scripts\\python.exe',
            args=[
                "MCP\\Server\\weather.py"
            ]
        )
        mcp_tool = McpToolSpec(mcp_client)
        tools = await mcp_tool.to_tool_list_async()
        self._agent = FunctionAgent(
            tools=tools,
            llm=llm,
            system_prompt='/no_think\nYou are Weathermatic a useful assistant that can help answering USA weather related queries.'
        )
        self._ctx = Context(self._agent)

    async def process_query(self, query: str) -> str:
        response = 'Agent not initialized!'
        if self._agent:
            response = (await self._agent.run(query, ctx=self._ctx)).response.content
        return response

    async def chat_loop(self):
        print("\nLlama Index Agent Started!")
        print("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\n" + response)
            except Exception as e:
                print(f"\nError: {str(e)}")


async def main():
    agent = LlamaIndexAgent()
    await agent.setup()
    await agent.chat_loop()

if __name__ == "__main__":
    import sys
    asyncio.run(main())
