import asyncio
from llama_index.core import VectorStoreIndex
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.readers.markitdown import MarkItDownReader
from openai import OpenAI
import os

base_dir = os.path.dirname(__file__)
#file_path = os.path.join(base_dir, "context", "file", "Requirements.md")
file_path = r'C:\Users\VMARTI19\OneDrive - Visteon\Documentos\02._Projects\IA Trainings\Testrack Assistant\context\files\Requirements.md'

class LlamaIndexAgent:
    MODEL =  "qwen2.5-14b-instruct" # "llama3:latest"
    MD_MODEL = "mistral-7b-instruct-v0.3" # "mistral-small3.1:latest"
    EMBED_MODEL = "nomic-embed-text:latest" # "text-embedding-nomic-embed-text-finetuned"
    API_KEY = "lmstudio"
    API_BASE = "http://172.18.32.1:1234/v1" # "http://localhost:11434"
    EMBED_API_BASE = "http://localhost:11434" # "http://172.18.32.1:1234/v1"

    def __init__(self):
        self._agent = None
        self._ctx = None
        self._query_engine = None

    async def setup(self):
        llm = OpenAILike(
            model=self.MODEL, 
            api_base=self.API_BASE,
            api_key=self.API_KEY,
            timeout=600,
            is_chat_model=True,
            is_function_calling_model=True
        )
        embed = OllamaEmbedding(model_name=self.EMBED_MODEL)
        code_llm = OpenAI(base_url=self.API_BASE,api_key=self.API_KEY)
        #documents = MarkItDownReader().load_data("context/file", llm_client=image_llm,llm_model='mistral-small3.1:latest')
        documents = MarkItDownReader().load_data(file_path, llm_client=code_llm,llm_model=self.MD_MODEL)
        index = VectorStoreIndex.from_documents(
            documents,
            embed_model=embed,
            show_progress=True
        )
        self._query_engine = index.as_query_engine(llm=llm)
        self._agent = AgentWorkflow.from_tools_or_functions(
            [self.search_documents],
            llm=llm,
            system_prompt='/no_think\nYou are VCDT Helper a useful assistant that can help answering user queries regarding issues and FAQs related to VCDT'
        )
        self._ctx = Context(self._agent)

    async def search_documents(self, query: str) -> str:
        """Useful for answering natural language wuestion about VCDT Common issues and FAQs"""
        resp = await self._query_engine.aquery(query)
        return resp.response
    
    async def process_query(self, query: str) -> str:
        response = 'Agent not initialized'
        if self._agent:
            agent_response = await self._agent.run(query, ctx=self._ctx)
            response = agent_response.response.content
            
        return response
    
    async def chat_loop(self):
        print("\nLlama Index Agent Started!")
        print("Type your queries or 'quit' to exit")
        while True:
            try:
                query =input("\nQuery: ").strip()
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
    asyncio.run(main())