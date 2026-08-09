import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

try:
    from .parser_engine import parse_file
    from .graph_builder import CodeGraph
    from .vector_search import get_embedding, search_code
except ImportError:
    from parser_engine import parse_file
    from graph_builder import CodeGraph
    from vector_search import get_embedding, search_code

app = FastAPI(title="CodeKG - Code Knowledge Graph API")

# Enable CORS for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory graph state & embeddings cache
current_graph = None
node_embeddings = {}

# Directories to ignore during scanning for maximum speed
IGNORE_DIRS = {
    "node_modules", "venv", ".venv", "__pycache__", ".git",
    "dist", "build", ".gemini", ".idea", ".vscode", "site-packages"
}


class ScanRequest(BaseModel):
    repo_path: str = "test_repo"


class SearchRequest(BaseModel):
    query: str


@app.get("/")
def read_root():
    """Serve the single-file web dashboard."""
    static_html = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_html):
        return FileResponse(static_html)
    return {"message": "CodeKG API active. Visit /api/graph for graph data."}


@app.post("/api/scan")
def scan_repo(req: ScanRequest):
    """Scan code repository, parse AST entities, build NetworkX graph, and embed functions."""
    global current_graph, node_embeddings

    start_time = time.time()
    
    # Clean up input path (handle quotes & slashes)
    clean_path = req.repo_path.strip('"').strip("'").strip()
    
    base_dir = os.path.dirname(__file__)
    repo_root = os.path.join(base_dir, clean_path)
    if not os.path.exists(repo_root):
        repo_root = os.path.abspath(clean_path)

    print("\n==================================================")
    print(f"[SCAN START] Target directory: {repo_root}")

    if not os.path.exists(repo_root):
        print(f"[ERROR] Repository path '{repo_root}' not found!")
        print("==================================================\n")
        raise HTTPException(status_code=404, detail=f"Repository path '{clean_path}' not found.")

    # 1. Parse all .py and .js files recursively (skipping heavy vendor dirs)
    parsed_files = []
    for root, dirs, files in os.walk(repo_root):
        # Prune ignored directories in-place for fast scanning
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file_name in files:
            if file_name.endswith((".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".hpp", ".c", ".h", ".cc", ".cxx")):
                file_path = os.path.join(root, file_name)
                parsed_files.append(parse_file(file_path))

    print(f"[PARSING COMPLETE] Processed {len(parsed_files)} source files.")

    # 2. Build graph using CodeGraph
    graph_obj = CodeGraph()
    graph_obj.build_graph(parsed_files)
    current_graph = graph_obj

    graph_data = graph_obj.to_dict()
    print(f"[GRAPH ENGINE] Constructed DiGraph with {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges.")

    # 3. Generate embeddings for function/class nodes (for vector search)
    node_embeddings = {}
    for node in graph_data["nodes"]:
        if node.get("type") in {"Function", "Class"}:
            code_text = node.get("code", "") or node.get("label", "")
            node_embeddings[node["id"]] = get_embedding(code_text)

    elapsed = time.time() - start_time
    print(f"[VECTOR ENGINE] Indexed embeddings for {len(node_embeddings)} function entities.")
    print(f"[SCAN COMPLETE] Successfully built graph in {elapsed:.2f}s!")
    print("==================================================\n")

    return {
        "status": "success",
        "nodes": len(graph_data["nodes"]),
        "edges": len(graph_data["edges"]),
        "elapsed_seconds": round(elapsed, 2)
    }


@app.get("/api/graph")
def get_graph():
    """Return graph nodes and edges as JSON."""
    if current_graph is None:
        # Auto-scan default test repo on first load if uninitialized
        scan_repo(ScanRequest(repo_path="test_repo"))
    return current_graph.to_dict()


@app.get("/api/blast-radius")
def get_blast_radius(node_id: str):
    """Return all upstream caller node IDs impacted by a change in node_id."""
    if current_graph is None:
        return []
    return current_graph.calculate_blast_radius(node_id)


@app.get("/api/cycles")
def get_cycles():
    """Return strongly connected components representing circular call dependencies."""
    if current_graph is None:
        return []
    return current_graph.get_circular_dependencies()


@app.post("/api/search")
def run_search(req: SearchRequest):
    """Run cosine similarity vector search over function embeddings."""
    if not node_embeddings:
        return []
    results = search_code(req.query, node_embeddings, top_k=5)
    return [{"node_id": node_id, "score": score} for node_id, score in results]


@app.get("/health")
def health():
    return {"status": "healthy"}
