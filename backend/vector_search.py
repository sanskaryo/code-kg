import os
import numpy as np


def get_embedding(text: str) -> list:
    """Generate embedding vector using OpenAI API if key exists, otherwise a simple local frequency vector."""
    if not text:
        return [0.0] * 10

    # 1. Try OpenAI API if OPENAI_API_KEY is available
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            res = client.embeddings.create(model="text-embedding-3-small", input=text)
            return list(res.data[0].embedding)
        except Exception:
            pass

    # 2. Fallback local vectorization (10-dim word hash vector)
    words = text.lower().split()
    vec = [0.0] * 10
    for word in words:
        idx = hash(word) % 10
        vec[idx] += 1.0
    return vec


def cosine_similarity(a: list, b: list) -> float:
    """Calculate Cosine Similarity: (a . b) / (|a| * |b|) using raw NumPy."""
    a_arr = np.array(a, dtype=float)
    b_arr = np.array(b, dtype=float)

    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))


def search_code(query_str: str, node_embeddings_dict: dict, top_k: int = 5) -> list:
    """Search code snippets by computing cosine similarity between query vector and node vectors."""
    query_vec = get_embedding(query_str)
    results = []

    for node_id, vector in node_embeddings_dict.items():
        score = cosine_similarity(query_vec, vector)
        results.append((node_id, score))

    # Sort descending by similarity score
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
