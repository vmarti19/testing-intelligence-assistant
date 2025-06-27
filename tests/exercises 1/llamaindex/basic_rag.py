import asyncio
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.openai_like import OpenAILike


class LlamaIndexAgent:
    MODEL = 'qwen3:32b'
    EMBED_MODEL = 'nomic-embed-text:latest'
    API_KEY = os.getenv("VISTEON_OLLAMA_TOKEN")

    def __init__(self):
        self._agent = None
        self._ctx = None
        self._query_engine = None
   
    async def setup(self):
        llm = OpenAILike(
            model=self.MODEL, api_base='http://chipd120.vistcorp.ad.visteon.com:8000/v1', api_key=self.API_KEY, timeout=600,
            is_chat_model=True, is_function_calling_model=True
        )
        embed = OllamaEmbedding(self.EMBED_MODEL)
        documents = SimpleDirectoryReader("llamaindex/docs", recursive=True).load_data(show_progress=True)
        index = VectorStoreIndex.from_documents(
            documents,
            embed_model=embed,
            show_progress=True
        )
        self._query_engine = index.as_query_engine(llm=llm)
        self._agent = AgentWorkflow.from_tools_or_functions(
            [self.search_documents],
            llm=llm,
            system_prompt='/no_think\nYou are VCDT Helper a useful assistant that can help answering user queries regarding common issues, FAQs and other subjects related to VCDT.'
        )
        self._ctx = Context(self._agent)

    async def search_documents(self, query: str) -> str:
        """Useful for answering natural language questions about VCDT Common issues and FAQs."""
        resp = await self._query_engine.aquery(query)
        return resp.response

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
