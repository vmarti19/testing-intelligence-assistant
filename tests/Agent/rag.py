import faiss
import numpy as np
import tqdm
import asyncio
from ollama import Client

import subprocess

MODEL = 'qwen2.5-coder:7b-instruct-q4_0'
MODEL_2 = 'nomic-embed-text:latest'

def is_model_installed(model_name):
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return model_name in result.stdout
    except Exception as e:
        print(f"Error al verificar modelos instalados: {e}")
        return False

def pull_model(model_name):
    try:
        subprocess.run(['ollama', 'pull', model_name], check=True)
        print(f"Modelo '{model_name}' descargado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al hacer pull del modelo: {e}")


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
    
 
    def __init__(self):
        self._messages = []
        self.client = Client(host='http://localhost:11434')
        self.vectordb = self._init_vectordb()
 
    def _init_vectordb(self):
        with open(r'C:\testrack\test\README.md', encoding='utf-8') as f:
            text = f.read()
        chunks = []
        for c in text.split('\n\n'):
            c = c.strip()
            if len(c) > 500:
                for i in range(0, len(c), 500):
                    chunks.append(c[i:i+500])
            else:
                chunks.append(c)
        return VectorDB(chunks, self._embed_fn)
 
    def _embed_fn(self, t):
        resp = self.client.embeddings(model=MODEL, prompt=t)
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

        print("\nAssistant: ", end='', flush=True)
        full_response = ""
        response = self.client.chat(model=MODEL, messages=self._messages, stream=True, options={'temperature': 0.15})

        for chunk in response:
            content = chunk['message']['content']
            print(content, end='', flush=True)
            full_response += content

        self._messages.append({
            "role": "assistant",
            "content": full_response
        })

        return full_response

 
    async def main_loop(self):
        print("\nRAG Chat Started!")
        print("Type your queries or 'quit' to exit.")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                #print("\nAssistant: " + response)
            except Exception as e:
                print(f"\nError: {str(e)}")
 
async def main():
    chat = ChatHandler()
    await chat.main_loop()
 
if __name__ == "__main__":

    if not is_model_installed(MODEL):
        print(f"Modelo '{MODEL}' no está instalado. Descargando...")
        pull_model(MODEL)
    else:
        print(f"Modelo '{MODEL}' ya está instalado.")

    asyncio.run(main())