import os
import numpy as np


def get_embedding(text: str):
    if not text:
        return []

    if os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            res = client.embeddings.create(model="text-embedding-3-small", input=text)
            return list(res.data[0].embedding)
        except Exception:
            pass

    return [float(len(text.split()))] + [0.0] * 9


def cosine_similarity(a, b):
    a_arr = np.array(a)
    b_arr = np.array(b)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))


def search_code(query_str, node_embeddings_dict, top_k=5):
    query_vec = get_embedding(query_str)
    results = []
    for node_id, vector in node_embeddings_dict.items():
        score = cosine_similarity(query_vec, vector)
        results.append((node_id, score))

    results.sort(key=lambda item: item[1], reverse=True)
    return results[:top_k]
