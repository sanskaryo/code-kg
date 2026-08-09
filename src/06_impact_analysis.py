import argparse
import os
import sys
from pathlib import Path

# Add parent directory to sys.path to import backend modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.graph_builder import CodeGraph
from backend.parser_engine import parse_file


def main():
    parser = argparse.ArgumentParser(description="Impact Analysis / Blast Radius CLI")
    parser.add_argument("--function", "-f", type=str, default="parse", help="Target function or node ID keyword")
    parser.add_argument("--dir", "-d", type=str, default="backend/test_repo", help="Target repository folder")
    args = parser.parse_args()

    print("--- Impact Analysis / Blast Radius ---")
    print(f"Target Keyword: '{args.function}' | Repository: '{args.dir}'")

    parsed_files = []
    for root, _, files in os.walk(args.dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".hpp", ".c", ".h"}:
                filepath = os.path.join(root, file)
                parsed_files.append(parse_file(filepath))

    cg = CodeGraph()
    cg.build_graph(parsed_files)

    # Match target node ID
    target_id = None
    for n in cg.graph.nodes:
        if args.function.lower() in n.lower():
            target_id = n
            break

    if not target_id:
        print(f"Error: Function/Entity matching '{args.function}' not found in graph.")
        print(f"Available nodes: {list(cg.graph.nodes)}")
        return

    impacted = cg.calculate_blast_radius(target_id)
    print(f"\nSelected Node: {target_id}")
    print(f"Impacted Upstream Callers / Dependencies ({len(impacted)}):")
    for item in impacted:
        print(f"  • {item}")


if __name__ == "__main__":
    main()
