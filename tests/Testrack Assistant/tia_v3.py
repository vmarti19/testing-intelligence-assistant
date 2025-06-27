import asyncio
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.readers.markitdown import MarkItDownReader
import os
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
import re
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "files")

class LlamaIndexAgent:
    MODEL = 'qwen3:8b'
    MODEL_MD = "mistral-small3.1:latest"
    MODEL_EMBED = "nomic-embed-text:latest" 
    API_KEY = "ollama"
    API_BASE = "http://localhost:11434/v1"

    client_base = Ollama(MODEL, request_timeout=600)

    def __init__(self):
        self._agent = None
        self._ctx = None
        self._query_engine = None
        self._messages =[
            ChatMessage(role="system", content="/no_think\nYou are a helpful assistant.")
        ]

    async def setup(self):
        client_openai = OpenAILike(
            model=self.MODEL, api_base=self.API_BASE, api_key=self.API_KEY, timeout=600,
            is_chat_model=True, is_function_calling_model=True
        )
        embed = OllamaEmbedding(model_name=self.MODEL_EMBED)
        #requirement_doc = MarkItDownReader().load_data(requirement_path, llm_client=self.client_base,llm_model=self.MODEL_MD)
        documents = SimpleDirectoryReader(file_path, recursive=True).load_data(show_progress=True)
        index = VectorStoreIndex.from_documents(documents,embed_model=embed,show_progress=True)
        self._query_engine = index.as_query_engine(llm=client_openai)
        self._agent = AgentWorkflow.from_tools_or_functions(
            [self.search_documents],
            llm=client_openai,
            system_prompt='/no_think\nYou are a development assistant who can generate code, tests, and execute scripts using MCP tools according with the Requirement.md file.'
        )
        self._ctx = Context(self._agent)

    async def search_documents(self, query: str) -> str:
        """Useful for answering natural language  or FAQs about the Requirement"""
        resp = await self._query_engine.aquery(query)
        return resp.response

    async def process_query(self, query: str) -> str:
        response = 'Agent not initialized'
        #self._messages.append(ChatMessage(role="user", content= query))
        if self._agent:
            agent_response = await self._agent.run(query, ctx=self._ctx)
            response = re.sub(r"<think>.*?</think>\n\n", "", agent_response.response.content, flags=re.DOTALL)
        return response
            #response = self.client_base.chat(messages=self._messages)
            #self._messages.append(response.message)
    
    async def chat_loop(self):
        print("\nLlama Index Agent Started!")
        print("Type your queries or 'quit' to exit")
        while True:
            try:
                query =input("\nUser: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\nSystem: " + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

async def main():
    agent = LlamaIndexAgent()
    await agent.setup()
    await agent.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())