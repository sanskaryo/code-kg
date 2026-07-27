import os
from typing import Dict, List, Tuple

import networkx as nx

from complexity import get_complexity_risk, get_cyclomatic_complexity


class CodeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_embeddings = {}

    def build_graph(self, parsed_files_data: List[Dict]) -> nx.DiGraph:
        self.graph = nx.DiGraph()
        for item in parsed_files_data:
            file_path = item.get("file_path", "")
            file_name = os.path.basename(file_path)
            base_id = file_name.replace(".", "_")

            module_node_id = f"module:{base_id}"
            self.graph.add_node(
                module_node_id,
                label=file_name,
                type="Module",
                file=file_path,
                code=item.get("code", ""),
                complexity=1,
            )

            for func in item.get("functions", []):
                node_id = f"func:{base_id}:{func['name']}"
                self.graph.add_node(
                    node_id,
                    label=func["name"],
                    type="Function",
                    file=file_path,
                    code=func.get("code", ""),
                    complexity=get_cyclomatic_complexity(func.get("code", "")),
                )
                self.graph.add_edge(module_node_id, node_id, type="DEFINES")

            for cls in item.get("classes", []):
                node_id = f"class:{base_id}:{cls['name']}"
                self.graph.add_node(
                    node_id,
                    label=cls["name"],
                    type="Class",
                    file=file_path,
                    code=cls.get("code", ""),
                    complexity=get_cyclomatic_complexity(cls.get("code", "")),
                )
                self.graph.add_edge(module_node_id, node_id, type="DEFINES")

            for imp in item.get("imports", []):
                imp_name = imp.get("name", "")
                if imp_name:
                    imp_node_id = f"import:{base_id}:{imp_name}"
                    self.graph.add_node(
                        imp_node_id,
                        label=imp_name,
                        type="Import",
                        file=file_path,
                        code=imp_name,
                        complexity=1,
                    )
                    self.graph.add_edge(module_node_id, imp_node_id, type="IMPORTS")

            for call in item.get("calls", []):
                call_name = call.get("name", "")
                if not call_name:
                    continue
                call_node_id = f"call:{base_id}:{call_name}"
                self.graph.add_node(
                    call_node_id,
                    label=call_name,
                    type="Call",
                    file=file_path,
                    code=call_name,
                    complexity=1,
                )
                self.graph.add_edge(module_node_id, call_node_id, type="CALLS")

        for node_id in list(self.graph.nodes()):
            attrs = self.graph.nodes[node_id]
            attrs["risk"] = get_complexity_risk(attrs.get("complexity", 1))

        return self.graph

    def get_circular_dependencies(self) -> List[List[str]]:
        cycles = []
        for comp in nx.strongly_connected_components(self.graph):
            if len(comp) > 1:
                cycles.append(sorted(list(comp)))
        return cycles

    def calculate_blast_radius(self, start_node_id: str) -> List[str]:
        if start_node_id not in self.graph:
            return []

        rev_graph = self.graph.reverse()
        try:
            upstream = nx.descendants(rev_graph, start_node_id)
        except Exception:
            upstream = []

        result = [start_node_id] + sorted(list(upstream))
        return result

    def to_json(self) -> Dict:
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            nodes.append({"id": node_id, "label": attrs.get("label", node_id), "type": attrs.get("type", "Node"), "file": attrs.get("file", ""), "code": attrs.get("code", ""), "complexity": attrs.get("complexity", 1), "risk": attrs.get("risk", "low")})

        edges = []
        for src, dst, attrs in self.graph.edges(data=True):
            edges.append({"source": src, "target": dst, "type": attrs.get("type", "REL")})

        return {"nodes": nodes, "edges": edges}
