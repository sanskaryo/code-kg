import os
from typing import Dict, List
import networkx as nx

try:
    from .complexity import get_cyclomatic_complexity, get_complexity_risk
except ImportError:
    from complexity import get_cyclomatic_complexity, get_complexity_risk


class CodeGraph:
    """Builds and analyzes code dependency graphs using NetworkX."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, parsed_files_data: List[Dict]) -> nx.DiGraph:
        """Construct graph nodes (Modules, Functions, Classes) and directed edges."""
        self.graph = nx.DiGraph()

        # Step 1: Create nodes for all files and defined entities
        for item in parsed_files_data:
            file_path = item.get("file_path", "")
            file_name = os.path.basename(file_path)
            base_id = file_name.replace(".", "_")

            # Module Node
            module_id = f"module:{base_id}"
            self.graph.add_node(
                module_id,
                label=file_name,
                type="Module",
                file=file_path,
                code=item.get("code", ""),
                complexity=1,
                risk="low"
            )

            # Function Nodes
            for func in item.get("functions", []):
                func_id = f"func:{base_id}:{func['name']}"
                comp = get_cyclomatic_complexity(func.get("code", ""))
                self.graph.add_node(
                    func_id,
                    label=func["name"],
                    type="Function",
                    file=file_path,
                    code=func.get("code", ""),
                    complexity=comp,
                    risk=get_complexity_risk(comp)
                )
                # Module DEFINES Function
                self.graph.add_edge(module_id, func_id, type="DEFINES")

            # Class Nodes
            for cls in item.get("classes", []):
                cls_id = f"class:{base_id}:{cls['name']}"
                comp = get_cyclomatic_complexity(cls.get("code", ""))
                self.graph.add_node(
                    cls_id,
                    label=cls["name"],
                    type="Class",
                    file=file_path,
                    code=cls.get("code", ""),
                    complexity=comp,
                    risk=get_complexity_risk(comp)
                )
                # Module DEFINES Class
                self.graph.add_edge(module_id, cls_id, type="DEFINES")

            # Import Nodes
            for imp in item.get("imports", []):
                imp_name = imp.get("name", "")
                if imp_name:
                    imp_id = f"import:{base_id}:{imp_name}"
                    self.graph.add_node(
                        imp_id,
                        label=imp_name,
                        type="Import",
                        file=file_path,
                        code=imp_name,
                        complexity=1,
                        risk="low"
                    )
                    self.graph.add_edge(module_id, imp_id, type="IMPORTS")

            # Call Nodes / Edges
            for call in item.get("calls", []):
                call_name = call.get("name", "")
                if call_name:
                    call_id = f"call:{base_id}:{call_name}"
                    if not self.graph.has_node(call_id):
                        self.graph.add_node(
                            call_id,
                            label=call_name,
                            type="Call",
                            file=file_path,
                            code=call_name,
                            complexity=1,
                            risk="low"
                        )
                    self.graph.add_edge(module_id, call_id, type="CALLS")

        return self.graph

    def calculate_blast_radius(self, start_node_id: str) -> List[str]:
        """Find all upstream nodes impacted if start_node_id breaks (using reversed graph traversal)."""
        if start_node_id not in self.graph:
            return []

        # Reverse graph so edge A -> B becomes B -> A (finding callers of B)
        reversed_graph = self.graph.reverse()
        upstream = nx.descendants(reversed_graph, start_node_id)
        return [start_node_id] + sorted(list(upstream))

    def get_circular_dependencies(self) -> List[List[str]]:
        """Identify strongly connected components with >1 node (circular dependency loops)."""
        cycles = []
        for component in nx.strongly_connected_components(self.graph):
            if len(component) > 1:
                cycles.append(sorted(list(component)))
        return cycles

    def to_dict(self) -> Dict:
        """Serialize graph to dictionary for API/JSON responses."""
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": attrs.get("label", node_id),
                "type": attrs.get("type", "Node"),
                "file": attrs.get("file", ""),
                "code": attrs.get("code", ""),
                "complexity": attrs.get("complexity", 1),
                "risk": attrs.get("risk", "low")
            })

        edges = []
        for src, dst, attrs in self.graph.edges(data=True):
            edges.append({
                "source": src,
                "target": dst,
                "type": attrs.get("type", "REL")
            })

        return {"nodes": nodes, "edges": edges}

    def to_json(self) -> Dict:
        """Alias for compatibility."""
        return self.to_dict()
