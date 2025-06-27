import asyncio
import faiss
import numpy as np
import os
import tqdm
from ollama import Client

class VectorDB:
    def __init__(self, texts, embed_fn):
        self.texts = texts
        self.embed_fn = embed_fn
        self.embeddings = self._embed_texts(texts)
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def _embed_texts(self, texts):
        embeddings = []
        for t in tqdm.tqdm(texts, desc="Embedding Chunks"):
            embeddings.append(self.embed_fn(t))
        embeddings = np.vstack(embeddings)
        return embeddings.astype('float32')

    def search(self, query, top_k=3):
        q_emb = self.embed_fn(query).astype('float32').reshape(1, -1)
        _, I = self.index.search(q_emb, top_k)
        texts = []
        for i in I[0]:
            texts.append(self.texts[i])
        return texts

class ChatHandler:
    MODEL = 'qwen3-no_think:8b'
    EMBED_MODEL = 'nomic-embed-text:latest'
    API_KEY = f'Bearer {os.getenv("VISTEON_OLLAMA_TOKEN")}'

    def __init__(self):
        self._messages = [{
            "role": "system",
            "content": "You are a helpful assistant that can answer questions based on the provided context.\n"
                       "Don't provide any information that is not in the context.\n"
                       "If you don't know the answer, say 'I don't know'."
        }]
        self.client = Client(host='http://chipd120.vistcorp.ad.visteon.com:8000', headers={'Authorization': self.API_KEY})
        self.embed_client = Client(host='http://localhost:11434')
        self.vectordb = self._init_vectordb()

    def _init_vectordb(self):
        with open('rag/CommonIssuesAndFAQ.md', encoding='utf-8') as f:
            text = f.read()
        chunks = []
        for c in text.split('\n\n'):
            c = c.strip()
            if not c:
                continue
            if len(c) > 500:
                for i in range(0, len(c), 500):
                    chunks.append(c[i:i+500])
            else:
                chunks.append(c)
        return VectorDB(chunks, self._embed_fn)

    def _embed_fn(self, t):
        resp = self.embed_client.embeddings(model=self.EMBED_MODEL, prompt=t)
        resp = np.array(resp['embedding'])
        return resp

    async def process_query(self, query: str) -> str:
        context_chunks = self.vectordb.search(query, top_k=3)
        context = '\n'.join(context_chunks)
        full_query = f"Context:\n{context}\n\nUser Query: {query}"
        self._messages.append({
            "role": "user",
            "content": full_query
        })
        response = self.client.chat(model=self.MODEL, messages=self._messages, options={'temperature': 0.15})
        self._messages.append({
            "role": response.message.role,
            "content": response.message.content
        })
        return response.message.content

    async def main_loop(self):
        print("\nRAG Chat Started!")
        print("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print("\nAssistant: " + response)
            except Exception as e:
                print(f"\nError: {str(e)}")

async def main():
    chat = ChatHandler()
    await chat.main_loop()

if __name__ == "__main__":
    asyncio.run(main())
