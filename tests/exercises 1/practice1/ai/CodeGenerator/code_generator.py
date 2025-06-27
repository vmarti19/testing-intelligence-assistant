import asyncio
import json
import os.path
import shutil
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from ollama import Client

class MCPClient:
    MODEL = 'qwen3-no_think:32b'
    URL = 'http://chipd120.vistcorp.ad.visteon.com:8000'
    API_KEY = f'Bearer {os.getenv("VISTEON_OLLAMA_TOKEN")}'
    MAX_TOKENS = 8192
    
    def __init__(self, reqs, out_path):
        # Initialize session and client objects
        with open(reqs) as reqs_file:
            self.reqs = reqs_file.read()
        self.output_path = out_path
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None
        self.client = Client(host=self.URL, headers={'Authorization': self.API_KEY})
        self.available_tools = []
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
        os.makedirs(self.output_path)

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command='.venv\\Scripts\\python.exe',
            args=[
                "practice1\\ai\\MCPServers\\filesystem_server.py"
            ],
            env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()
        response = await self.session.list_tools()
        self.available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]

    async def process_query(self, query: str, system: str = None) -> str:
        messages = []
        if system:
            messages.append({
                "role": "system",
                "content": system
            })
        messages.append({
            "role": "user",
            "content": query
        })
        response = self.client.chat(model=self.MODEL, messages=messages,
                                    tools=self.available_tools, options={'temperature': 0.15})
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
                    "content": json.dumps(result.content[0].text)
                })
            response = self.client.chat(model=self.MODEL, messages=messages,
                                        tools=self.available_tools, options={'temperature': 0.15})
        final_text.append(response.message.content)
        return "\n".join(final_text)

    async def cleanup(self):
        await self.exit_stack.aclose()

    async def generate_from_reqs(self):
        response = await self.process_query(
            'Generate a python script that fulfills the following requirements:\n'
            f'```\n{self.reqs}\n```'
            f'The generated script must be written to file: {self.output_path}\\main.py',
            '/no_think\nYou are an expert python programmer. You can write perfect python code from '
            'text requirements.\n'
            'Don\'t use unnecessary semicolons at the end of the line.\n'
            'Keep long lines in a single line it doesn\'t matter it is too long.\n'
            'Your generated code shall be written to a file.\n'
            'Use available tools to create the file. Verify that the tool_call content is valid.'
        )
        print(response)

async def main():
    client = MCPClient(
        'practice1\\input\\Requirements.md',
        'practice1\\output\\src',
    )
    await client.connect_to_server()
    await client.generate_from_reqs()
    await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())