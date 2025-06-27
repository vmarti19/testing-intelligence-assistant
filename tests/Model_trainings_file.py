import asyncio
from ctypes import Array
import faiss
import numpy as np
import os
import spacy
import tqdm
from ollama import Client
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Set

class GraphNode:
    def __init__(self, id: int, text: str, embedding: np.ndarray):
        self.id = id
        self.text = text
        self.embedding = embedding
        self.neighbors: Set[int] = set()
 
    def add_neighbor(self, node_id: int):
        self.neighbors.add(node_id)
 
    def __repr__(self):
        return f"Node(id={self.id}, text={self.text[:30]}..., neighbors={len(self.neighbors)})"
    
class GraphRAG:
    def __init__(self, texts, embed_fn, similarity_threshold=0.6):
        self.embed_fn = embed_fn
        self.similarity_threshold = similarity_threshold
        self.nodes: Array[GraphNode] = []
        self.nlp = spacy.load("en_core_web_sm")
        self._build_graph(texts)
        self.embeddings = np.vstack([node.embedding for node in self.nodes])
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings.astype('float32'))

    def _extract_entities_and_keywords(self, text: str) -> List[str]:
        doc = self.nlp(text)
        entities = [ent.text.lower() for ent in doc.ents]
        keywords = [token.lemma_.lower() for token in doc 
                   if (token.pos_ in ["NOUN", "PROPN", "ADJ"]) 
                   and not token.is_stop and len(token.text) > 2]
        return list(set(entities + keywords))
 
    def _build_graph(self, texts: List[str]):
        print("Building knowledge graph...")
        embeddings = []
        for i, text in enumerate(tqdm.tqdm(texts, desc="Creating nodes")):
            embedding = self.embed_fn(text).astype('float32')
            embeddings.append(embedding)
            node = GraphNode(id=i, text=text, embedding=embedding)
            self.nodes.append(node)
        embeddings = np.vstack(embeddings)
        similarities = cosine_similarity(embeddings)
        edge_count = 0
        for i in tqdm.tqdm(range(len(embeddings)), desc="Creating edges (semantic)"):
            for j in range(i+1, len(embeddings)):
                if similarities[i, j] > self.similarity_threshold:
                    self.nodes[i].add_neighbor(j)
                    self.nodes[j].add_neighbor(i)
                    edge_count += 1
        if self.nlp:
            for i in tqdm.tqdm(range(len(embeddings)), desc="Creating edges (entity-based)"):
                text_i = self.nodes[i].text
                entities_i = self._extract_entities_and_keywords(text_i.replace('#', ''))
                for j in range(i+1, len(embeddings)):
                    text_j = self.nodes[j].text
                    if j in self.nodes[i].neighbors and i in self.nodes[j].neighbors:
                        continue
                    entities_j = self._extract_entities_and_keywords(text_j.replace('#', ''))
                    shared_entities = set(entities_i).intersection(set(entities_j))
                    if len(shared_entities) >= 2:
                        self.nodes[i].add_neighbor(j)
                        self.nodes[j].add_neighbor(i)
                        edge_count += 1
        print(f"Knowledge graph built with {len(self.nodes)} nodes and {edge_count} edges")
    
    def search(self, query: str, top_k=3, use_graph_expansion=True) -> List[str]:
        q_emb = self.embed_fn(query).astype('float32').reshape(1, -1)
        _, I = self.index.search(q_emb, min(top_k, len(self.nodes)))
        result_ids = I[0].tolist()
        if use_graph_expansion:
            expanded_ids = set(result_ids)
            for node_id in result_ids:
                neighbors = self.nodes[node_id].neighbors
                expanded_ids.update(neighbors)
            if len(expanded_ids) > top_k:
                expanded_embeddings = np.vstack([self.nodes[id].embedding for id in expanded_ids])
                sims = cosine_similarity(q_emb, expanded_embeddings)[0]
                expanded_ids_list = list(expanded_ids)
                sorted_ids = [expanded_ids_list[i] for i in np.argsort(-sims)[:top_k]]
                result_ids = sorted_ids
        return [self.nodes[id].text for id in result_ids]

class ChatHandler:
    MODEL = 'qwen3:8b'
    EMBED_MODEL = 'nomic-embed-text:latest'
    API_KEY = f'Bearer {os.getenv("VISTEON_OLLAMA_TOKEN")}'
 
    def __init__(self):
        self._messages = [{
            "role": "system",
            "content": "/no_think\n"
                       "You are a helpful assistant that can answer questions based on the provided context.\n"
                       "Don't provide any information that is not in the context.\n"
                       "If you don't know the answer, say 'I don't know'."
        }]
        self.client = Client(host='http://localhost:11434')
        self.embed_client = Client(host='http://localhost:11434')
        self.graphrag = self._init_graphrag()
 
    def _init_graphrag(self):
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
        return GraphRAG(chunks, self._embed_fn)
 
    def _embed_fn(self, t):
        resp = self.embed_client.embeddings(model=self.EMBED_MODEL, prompt=t)
        resp = np.array(resp['embedding'])
        return resp
 
    async def process_query(self, query: str) -> str:
        context_chunks = self.graphrag.search(query, top_k=10, use_graph_expansion=True)
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
        print("\nGraphRAG Chat Started!")
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