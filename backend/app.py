import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .parser_engine import parse_file
    from .graph_builder import CodeGraph
    from .vector_search import get_embedding, search_code
except ImportError:  # pragma: no cover
    from parser_engine import parse_file
    from graph_builder import CodeGraph
    from vector_search import get_embedding, search_code

app = FastAPI(title="CodeKG")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_graph = None
node_embeddings = {}


class ScanRequest(BaseModel):
    repo_path: str


class SearchRequest(BaseModel):
    query: str


@app.post("/api/scan")
def scan_repo(req: ScanRequest):
    global current_graph, node_embeddings

    repo_root = os.path.join(os.path.dirname(__file__), req.repo_path)
    if not os.path.exists(repo_root):
        raise HTTPException(status_code=404, detail="repo not found")

    parsed_files = []
    for root, _, files in os.walk(repo_root):
        for file_name in files:
            if file_name.endswith((".py", ".js")):
                path = os.path.join(root, file_name)
                parsed_files.append(parse_file(path))

    graph_obj = CodeGraph()
    graph_obj.build_graph(parsed_files)
    current_graph = graph_obj

    node_embeddings = {}
    for node in graph_obj.to_json()["nodes"]:
        if node.get("type") == "Function":
            code_text = node.get("code", "")
            node_embeddings[node["id"]] = get_embedding(code_text)

    return {"status": "ok", "nodes": len(graph_obj.to_json()["nodes"]), "edges": len(graph_obj.to_json()["edges"])}


@app.get("/api/graph")
def get_graph():
    if current_graph is None:
        return {"nodes": [], "edges": []}
    return current_graph.to_json()


@app.get("/api/blast-radius")
def get_blast_radius(node_id: str):
    if current_graph is None:
        return []
    return current_graph.calculate_blast_radius(node_id)


@app.get("/api/cycles")
def get_cycles():
    if current_graph is None:
        return []
    return current_graph.get_circular_dependencies()


@app.post("/api/search")
def run_search(req: SearchRequest):
    if not node_embeddings:
        return []
    results = search_code(req.query, node_embeddings, top_k=5)
    return [{"node_id": node_id, "score": score} for node_id, score in results]


@app.get("/health")
def health():
    return {"status": "ok"}
