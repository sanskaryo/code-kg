import os
import sys
from pathlib import Path

# Add parent directory to sys.path to import backend modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.graph_builder import CodeGraph
from backend.parser_engine import parse_file


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "backend/test_repo"
    print(f"--- Building Code Knowledge Graph for '{target_dir}' ---")

    parsed_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".hpp", ".c", ".h"}:
                filepath = os.path.join(root, file)
                parsed_files.append(parse_file(filepath))

    cg = CodeGraph()
    cg.build_graph(parsed_files)
    graph_json = cg.to_json()

    print(f"\nGraph Construction Successful!")
    print(f"  • Total Nodes: {len(graph_json['nodes'])}")
    print(f"  • Total Edges: {len(graph_json['edges'])}")

    # Check for circular dependencies
    cycles = cg.get_circular_dependencies()
    print(f"  • Circular Dependency Loops: {len(cycles)}")
    for i, cycle in enumerate(cycles, 1):
        print(f"     Loop {i}: {' -> '.join(cycle)}")


if __name__ == "__main__":
    main()
