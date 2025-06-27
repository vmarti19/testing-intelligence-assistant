import faiss
import yaml
import numpy as np
import tqdm
import asyncio
from ollama import Client
import subprocess
import os
import threading
import itertools
import sys
import time

def spinner(msg, stop_event):
    for char in itertools.cycle('|/-\\'):
        if stop_event.is_set():
            break
        sys.stdout.write(f'\r{msg} {char}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * (len(msg) + 2) + '\r')

def is_model_installed(model_name):
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        return model_name in result.stdout
    except Exception as e:
        print(f"Error al verificar modelos instalados: {e}")
        return False

def pull_model(model_name):
    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner, args=(f"Descargando modelo '{model_name}'...", stop_event))
    spinner_thread.start()
    try:
        print(f"Intentando descargar el modelo '{model_name}'...")
        result = subprocess.run(['ollama', 'pull', model_name],check=True,capture_output=True,text=True,encoding='utf-8',errors='replace')
        stop_event.set()
        spinner_thread.join()
        print(result.stdout)
        print(f"Modelo '{model_name}' descargado correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"Error al hacer pull del modelo '{model_name}':")
        print(e.stderr)
    except FileNotFoundError:
        print("El comando 'ollama' no se encontró. ¿Está instalado y en tu PATH?")


def select_model(config):
    os.system('cls' if os.name == 'nt' else 'clear')
    models = config.get('models', [])

    if len(models) > 1:
        print("\nSelect a model available:")
        for idx, model in enumerate(models):
            print(f"{idx} - {model['name']}")

        while True:
            query = input("\nOpción (o escribe 'quit' para salir): ").strip()
            if query.lower() == 'quit':
                return 0
            if query.isdigit():
                idx = int(query)
                if 0 <= idx < len(models):
                    return idx
                print("La opción está fuera de rango.")
            else:
                print("Opción no válida, intenta de nuevo.")
    else:
        print(f"Modelo seleccionado: {models[0]['name']}")
        return 0

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
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        model_selected = select_model(config)
        self._messages = []
        self.model = config['models'][model_selected]['model']
        self.apiBase = config['models'][model_selected]['apiBase']
        if not is_model_installed(self.model):
            print(f"Model '{self.model}' is not pull yet. Pulling in local machine...")
            pull_model(self.model)
        else:
            print(f"Model '{self.model}' already pull.")
        self.client = Client(host=self.apiBase)
        self.vectordb = self._init_vectordb()
    
    def _init_vectordb(self):
        with open(r'C:\testrack\prj\ford_clusters\docs\indicators.md', encoding='utf-8') as f:
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
        resp = self.client.embeddings(model=self.model, prompt=t)
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
        response = self.client.chat(model=self.model, messages=self._messages, stream=True, options={'temperature': 0.15})

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
                #response = await self.process_query(query)
                await self.process_query(query)
                #print("\nAssistant: " + response)
            except Exception as e:
                print(f"\nError: {str(e)}")
 
async def main():
    chat = ChatHandler()
    await chat.main_loop()
 
if __name__ == "__main__":
    asyncio.run(main())