import os
import sys
from pathlib import Path

# Add parent directory to sys.path to import backend modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.graph_builder import CodeGraph
from backend.parser_engine import parse_file


def visualize():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "backend/test_repo"
    output_html = "code_kg_vis.html"
    print(f"--- Visualizing Code Knowledge Graph for '{target_dir}' ---")

    parsed_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".cpp", ".hpp", ".c", ".h"}:
                filepath = os.path.join(root, file)
                parsed_files.append(parse_file(filepath))

    cg = CodeGraph()
    cg.build_graph(parsed_files)

    try:
        from pyvis.network import Network

        net = Network(height="750px", width="100%", bgcolor="#0b0f19", font_color="#f1f5f9", directed=True)

        color_map = {
            "Module": "#3b82f6",
            "Class": "#10b981",
            "Function": "#f97316",
            "Import": "#a855f7",
            "Call": "#ec4899",
        }

        for node_id, data in cg.graph.nodes(data=True):
            ntype = data.get("type", "Module")
            label = data.get("label", node_id)
            color = color_map.get(ntype, "#94a3b8")
            title = f"Type: {ntype}<br/>File: {data.get('file', 'N/A')}<br/>Complexity: {data.get('complexity', 1)}"
            net.add_node(node_id, label=label, color=color, title=title)

        for u, v, data in cg.graph.edges(data=True):
            rel = data.get("type", "CONNECTED_TO")
            net.add_edge(u, v, title=rel)

        net.save_graph(output_html)
        print(f"Graph visualization saved successfully to: {os.path.abspath(output_html)}")
    except Exception as e:
        print(f"Pyvis visualization note ({e}). Saving summary HTML visualization...")
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(
                f"<html><body style='background:#0b0f19;color:#fff;font-family:sans-serif;'><h2>CodeKG Visual Summary</h2><p>Nodes: {len(cg.graph.nodes)} | Edges: {len(cg.graph.edges)}</p></body></html>"
            )
        print(f"Summary saved to {os.path.abspath(output_html)}")


if __name__ == "__main__":
    visualize()
