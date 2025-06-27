import asyncio
import os

from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ollama import Client


class MCPClient:
    MODEL = 'qwen3-no_think:8b'

    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None
        self.client = Client(host='http://chipd120.vistcorp.ad.visteon.com:8000',
                             headers={'Authorization': f'Bearer {os.getenv("VISTEON_OLLAMA_TOKEN")}'})

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command='.venv\\Scripts\\python.exe',
            args=[
                "MCP\\Server\\weather.py"
            ],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]
        response = self.client.chat(model=self.MODEL, messages=messages,
                                    tools=available_tools, options={'temperature': 0.15})

        final_text = []
        while response.message.tool_calls and len(response.message.tool_calls) > 0:
            for tool in response.message.tool_calls:
                tool_name = tool.function.name
                tool_args = tool.function.arguments
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                messages.append({
                    "role": "assistant",
                    "function_call": {
                        "name": tool_name,
                        "arguments": tool_args
                    }
                })
                messages.append({
                    "role": "tool",
                    "content": result.content[0].text
                })
            response = self.client.chat(model=self.MODEL, messages=messages,
                                        tools=available_tools)
        final_text.append(response.message.content)
        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP Client Started!")
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

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())