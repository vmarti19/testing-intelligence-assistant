import asyncio
import chromadb
import os
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.memory import Memory, StaticMemoryBlock, FactExtractionMemoryBlock, VectorMemoryBlock
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.workflow import Context
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.vector_stores.chroma import ChromaVectorStore
from support.MarkItDownReader import MarkItDownReader
from openai import OpenAI


class LlamaIndexAgent:
    MODEL = 'qwen3-no_think:32b'
    EMBED_MODEL = 'nomic-embed-text:latest'
    RERANK_MODEL = 'qwen3-no_think:8b'
    API_KEY = os.getenv("VISTEON_OLLAMA_TOKEN")
    VECTOR_DATABASE = 'llamaindex/vector_database'

    def __init__(self):
        self._agent = None
        self._ctx = None
        self._query_engine = None
        self._memory = None

    async def setup(self):
        llm = OpenAILike(
            model=self.MODEL, api_base='http://chipd120.vistcorp.ad.visteon.com:8000/v1', api_key=self.API_KEY, timeout=600,
            is_chat_model=True, is_function_calling_model=True
        )
        embed = OllamaEmbedding(self.EMBED_MODEL)
        image_llm = OpenAI(base_url="http://chipd120.vistcorp.ad.visteon.com:8000/v1", api_key=os.getenv("VISTEON_OLLAMA_TOKEN"))
        ranker_llm = OpenAILike(
            model=self.RERANK_MODEL, api_base='http://chipd120.vistcorp.ad.visteon.com:8000/v1', api_key=self.API_KEY, timeout=600,
            is_chat_model=True, is_function_calling_model=True
        )
        db = chromadb.PersistentClient(path=self.VECTOR_DATABASE)
        chroma_collection = db.get_or_create_collection("VCDT")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        if os.path.exists(self.VECTOR_DATABASE):
            index = VectorStoreIndex.from_vector_store(
                vector_store,
                embed_model=embed,
                show_progress=True
            )
        else:
            documents = MarkItDownReader().load_data("llamaindex/docs/", llm_client=image_llm, llm_model="mistral-small3.1:latest")
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex.from_documents(
                documents,
                embed_model=embed,
                show_progress=True,
                storage_context=storage_context
            )
        self._query_engine = index.as_query_engine(
            llm=llm,
            node_postprocessors=[
                LLMRerank(llm=ranker_llm, choice_batch_size=20, top_n=5)
            ]
        )
        mcp_client = BasicMCPClient(
            '.venv\\Scripts\\python.exe',
            args=[
                "MCP\\Server\\weather.py"
            ]
        )
        mcp_tool = McpToolSpec(mcp_client)
        tools = await mcp_tool.to_tool_list_async()
        tools.append(self.search_documents)
        self._agent = AgentWorkflow.from_tools_or_functions(
            tools,
            llm=llm,
            system_prompt='/no_think\nYou are VCDT Helper a useful assistant that can help answering user queries regarding common issues, FAQs and other subjects related to VCDT. But also you can help with USA weather queries.'
        )
        self._ctx = Context(self._agent)
        blocks = [
            StaticMemoryBlock(
                name="core_info",
                static_content="VCDT stands for Visteon Cluster Development Toolkit.",
                priority=0,
            ),
            FactExtractionMemoryBlock(
                name="extracted_info",
                llm=llm,
                max_facts=50,
                priority=1,
            ),
            VectorMemoryBlock(
                name="vector_memory",
                vector_store=vector_store,
                priority=2,
                embed_model=embed
            ),
        ]
        self._memory = Memory.from_defaults(session_id='chat', token_limit=40000, memory_blocks=blocks, insert_method="system")

    async def search_documents(self, query: str) -> str:
        """Useful for answering natural language questions about VCDT Common issues and FAQs."""
        resp = await self._query_engine.aquery(query)
        return resp.response

    async def process_query(self, query: str) -> str:
        response = 'Agent not initialized!'
        if self._agent:
            response = (await self._agent.run(query, ctx=self._ctx, memory=self._memory)).response.content
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
