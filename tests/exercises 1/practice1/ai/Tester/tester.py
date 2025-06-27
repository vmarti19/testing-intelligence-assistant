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

    def __init__(self, test, script, out_path):
        # Initialize session and client objects
        with open(test) as test_file:
            self.test = test_file.read()
        self.script = script
        self.output_path = out_path
        self.session: Array[Optional[ClientSession]] = [None, None]
        self.exit_stack = [AsyncExitStack(), AsyncExitStack()]
        self.stdio = [None, None]
        self.write = [None, None]
        self.client = Client(host=self.URL, headers={'Authorization': self.API_KEY})
        self.available_tools = []
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
        os.makedirs(self.output_path)

    async def connect_to_server(self):
        server_params = StdioServerParameters(
            command='mcp-proxy.exe',
            args=[
                "http://localhost:8585/sse"
            ],
            env=None
        )
        stdio_transport = await self.exit_stack[0].enter_async_context(stdio_client(server_params))
        self.stdio[0], self.write[0] = stdio_transport
        self.session[0] = await self.exit_stack[0].enter_async_context(ClientSession(self.stdio[0], self.write[0]))
        await self.session[0].initialize()
        response = await self.session[0].list_tools()
        self.available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]
        server_params_fs = StdioServerParameters(
            command='.venv\\Scripts\\python.exe',
            args=[
                "practice1\\ai\\MCPServers\\filesystem_server.py"
            ],
            env=None
        )
        stdio_transport_fs = await self.exit_stack[1].enter_async_context(stdio_client(server_params_fs))
        self.stdio[1], self.write[1] = stdio_transport_fs
        self.session[1] = await self.exit_stack[1].enter_async_context(ClientSession(self.stdio[1], self.write[1]))
        await self.session[1].initialize()
        response = await self.session[1].list_tools()
        for tool in response.tools:
            self.available_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })

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
                result = await self.session[0].call_tool(tool_name, tool_args)
                if result.isError and result.content[0].text.startswith('Unknown tool: '):
                    result = await self.session[1].call_tool(tool_name, tool_args)
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
            response = self.client.chat(model=self.MODEL, messages=messages, tools=self.available_tools,
                                        options={'temperature': 0.15})
        if response.message.content:
            final_text.append(response.message.content)
        return "\n".join(final_text)

    async def cleanup(self):
        await self.exit_stack[1].aclose()
        await self.exit_stack[0].aclose()

    async def test_script(self):
        response = await self.process_query(
            'Execute all the tests described in the following test plan:\n'
            f'```\n{self.test}\n```'
            f'The script to test is located in: {self.script}.\n'
            'The database will be generated on current path.\n'
            f'Generate a test report with the results of the tests and store it on: {self.output_path}\\report.md.\n.',
            '/no_think\nYou are an expert tester. You can execute a test plan step by step.'
            'To test the python script use one of the provided tools.\n'
            'When using tools verify that the tool_call content is valid.\n'
            'Finally generate a test report in markdown format with the results of the test.'
        )
        return response


async def main():
    client = MCPClient(
        'practice1\\output\\test\\test_cases.md',
        'practice1\\output\\src\\main.py',
        'practice1\\output\\report',
    )
    await client.connect_to_server()
    result = await client.test_script()
    await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())