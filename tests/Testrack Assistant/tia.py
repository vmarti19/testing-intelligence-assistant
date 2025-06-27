import asyncio
import json
import sys
import os
 
from typing import Optional
from contextlib import AsyncExitStack
 
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
 
from openai import OpenAI
from ollama import Client


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.stdio = None
        self.write = None
        #self.model = 'qwen2.5-coder:7b-instruct-q4_0' # Ollama
        #self.embed_model = 'nomic-embed-text:latest' # Ollama
        self.model = 'qwen2.5-coder-7b-instruct' # Open IA
        #self.client = Client(host='http://localhost:11434')
        self.client = OpenAI(base_url="http://10.137.58.215:1234/v1", api_key='lmstudio') # Open AI

    async def connect_to_server(self):
        script_path = os.path.abspath("mcp_tool.py")
        server_params = StdioServerParameters(
            command= sys.executable,
            args=[script_path],
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
        response = self.client.chat.completions.create(model=self.model , messages=messages,
                                                       tools=available_tools, max_tokens=1000)
 
        final_text = []
        for content in response.choices:
            if content.message.tool_calls and len(content.message.tool_calls) > 0:
                for tool in content.message.tool_calls:
                    tool_name = tool.function.name
                    tool_args = json.loads(tool.function.arguments)
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
                    response = self.client.chat.completions.create(model=self.model, messages=messages,
                                                                   tools=available_tools, max_tokens=1000)
                    if response.choices[0].message.content is not None:
                        final_text.append(response.choices[0].message.content)
                    elif len(result.content[0].text)>0:
                        final_text.append(result.content[0].text)

            else:
                final_text.append(content.message.content)
        return "\n".join(final_text)
 
    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        query = 'please create a script  based on the file: ../../input/Requirements.md  and save it with the name  tester.py in the path ../../output/test/'
        result= await client.process_query(query)
        print(result)
    finally:
        await client.cleanup()
 
if __name__ == "__main__":
    asyncio.run(main())