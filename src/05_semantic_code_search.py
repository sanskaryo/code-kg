import argparse
import os
import sys
from pathlib import Path

# Add parent directory to sys.path to import backend modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.graph_builder import CodeGraph
from backend.parser_engine import parse_file
from backend.vector_search import search_code


def main():
    parser = argparse.ArgumentParser(description="Semantic Code Search CLI")
    parser.add_argument("--query", "-q", type=str, default="error handling", help="Search query string")
    parser.add_argument("--dir", "-d", type=str, default="backend/test_repo", help="Target repository folder")
    args = parser.parse_args()

    print("--- Semantic Code Search ---")
    print(f"Query: '{args.query}' | Target: '{args.dir}'")

    parsed_files = []
    for root, _, files in os.walk(args.dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".hpp", ".c", ".h"}:
                filepath = os.path.join(root, file)
                parsed_files.append(parse_file(filepath))

    cg = CodeGraph()
    cg.build_graph(parsed_files)
    nodes = cg.to_json()["nodes"]

    results = search_code(args.query, nodes)
    print(f"\nTop {len(results)} Matches:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. Node: {r['node_id']} (Similarity: {r['score']*100:.1f}%)")


if __name__ == "__main__":
    main()
