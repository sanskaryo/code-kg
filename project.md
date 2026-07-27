

This instruction file explicitly commands the AI agent to generate the **complete codebase skeleton** while strictly adopting a **realistic student developer persona**—ensuring the code looks hand-coded, direct, free of generic AI docstrings, and easy for you to explain in an interview.

---

### Save the text below as `PROJECT_BUILDER.md` (or `.cursorrules`) in your project root:

```markdown
# MASTER PROJECT SPECIFICATION: Code Knowledge Graph (CodeKG)

## 1. AGENT INSTRUCTION & DEVELOPER PERSONA (CRITICAL)
You are acting as an AI coding assistant helping a final-year CS student build their solo capstone project in 5–7 days.

### STRICT CODING STYLE CONSTRAINTS:
1. **NO "AI-GENERATED" LOOK:**
   - DO NOT generate overly verbose enterprise docstrings (e.g., ban `"""This module represents the primary controller for processing AST trees..."""`).
   - Keep comments short, informal, and sparse—like a student typing quickly (e.g., `# fix this later`, `# convert bytes to string here`, `# handle edge case where name is empty`).
   - Use straightforward, practical variable names (`temp_list`, `func_map`, `res`, `out_graph`, `node_info`, `curr_node`, `item_data`) alongside standard domain terms (`target_id`, `ast_tree`).
   - AVOID unnecessary abstractions, design patterns, or factory classes. Write clean, readable, top-to-bottom procedural code and simple Python classes.

2. **NO HEAVY WRAPPER LIBRARIES:**
   - **ABSOLUTELY NO LANGCHAIN, LLAMAINDEX, OR HEAVY AGENT FRAMEWORKS.**
   - For Semantic Search: Use raw `openai` or `ollama` client to get embeddings, and write the **Cosine Similarity function directly using NumPy** (`np.dot(a, b) / (norm(a) * norm(b))`).
   - For Graph Math: Use native `networkx` functions and raw Python lists/dicts.

3. **COMPREHENSIVE CODE WRITING:**
   - Do NOT use placeholders like `# TODO: implement this later` or `// ... rest of code`. 
   - Write complete, fully functional, executable files for the entire project skeleton.

---

## 2. PROJECT OVERVIEW
A full-stack DevTool platform that parses Python and JavaScript repositories using `tree-sitter`, extracts code entities (Functions, Classes, Modules, Imports, Calls), constructs a multi-relational Directed Graph with `networkx`, runs graph algorithms (Tarjan's SCC for circular imports, BFS for Blast Radius, Cyclomatic Complexity scoring), exposes a FastAPI backend, and renders an interactive UI.

---

## 3. FILE SKELETON TO GENERATE

```text
code-kg/
├── backend/
│   ├── app.py                   # FastAPI server with REST endpoints
│   ├── parser_engine.py         # Tree-sitter AST parser (Python + JS)
│   ├── graph_builder.py         # NetworkX graph structure & DSA algorithms
│   ├── vector_search.py         # Raw NumPy cosine similarity & embedding search
│   ├── complexity.py            # Cyclomatic complexity score calculator
│   ├── requirements.txt         # Dependencies
│   └── test_repo/               # Sample code folder to test parsing
│       ├── main.py
│       ├── utils.py
│       └── app.js
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main dashboard layout & search bar
    │   ├── components/
    │   │   ├── GraphView.jsx    # Interactive graph renderer
    │   │   ├── DetailPanel.jsx  # Side drawer for code, complexity & blast radius
    │   │   └── SearchBar.jsx    # Semantic search input
    │   ├── main.jsx
    │   └── index.css            # Tailwind styling
    ├── package.json
    └── vite.config.js

```

---

## 4. DETAILED SPECIFICATIONS PER FILE

### File 1: `backend/requirements.txt`

Dependencies to include:

```text
tree-sitter==0.26.0
tree-sitter-python
tree-sitter-javascript
networkx
fastapi
uvicorn
pydantic
numpy
openai
python-dotenv

```

---

### File 2: `backend/parser_engine.py`

**Goal:** Parse `.py` and `.js` files using `tree-sitter`. Extract functions, classes, imports, and call targets.
**Style Rules:** Write practical, student-style recursive parsing loops.
**Core Functions:**

1. `parse_file(file_path: str)`: Loads raw bytes, determines language (`python` vs `javascript`), runs parser.
2. Recursively walks AST nodes looking for:
* Function definitions (`function_definition` in Python, `function_declaration` / `arrow_function` in JS).
* Class definitions (`class_definition` / `class_declaration`).
* Import statements (`import_statement`, `import_from_statement`).
* Function calls (`call` / `call_expression`).


3. Returns a structured dictionary of extracted entities for the graph builder.

---

### File 3: `backend/graph_builder.py`

**Goal:** Map extracted file dictionaries into a `networkx.DiGraph`. Implement core DSA algorithms.
**Style Rules:** Direct code, clear variables, minimal fluff.
**Core Class:** `CodeGraph`
**Key Methods:**

1. `build_graph(parsed_files_data)`:
* Creates nodes with attributes (`label`, `type`, `file`, `code`, `complexity`).
* Creates directed edges with types (`CALLS`, `IMPORTS`, `DEFINES`).


2. `get_circular_dependencies()`:
* Uses `nx.strongly_connected_components(self.graph)`.
* Filters components where `len(scc) > 1` (identifies circular call/import loops).


3. `calculate_blast_radius(start_node_id)`:
* Reverses graph edges (`self.graph.reverse()`) so caller-callee relationship is flipped.
* Runs `nx.descendants()` or BFS to find all upstream caller functions impacted if `start_node_id` breaks.


4. `to_json()`:
* Converts `self.graph` into a `{ nodes: [...], edges: [...] }` dict for React Flow / frontend graph libraries.



---

### File 4: `backend/complexity.py`

**Goal:** Calculate a simple Cyclomatic Complexity score ($M = E - N + 2P$) for code snippets.
**Implementation:**

* Write a function `get_cyclomatic_complexity(code_str: str) -> int`.
* Count decision points (`if`, `elif`, `for`, `while`, `except`, `case`, `&&`, `||`).
* Return integer complexity score (`1` to `10+`). Assign a risk level (`low`, `medium`, `high`).

---

### File 5: `backend/vector_search.py`

**Goal:** Pure NumPy-based semantic search across code function snippets. **NO LANGCHAIN.**
**Implementation:**

1. `get_embedding(text: str)`: Calls OpenAI API (`text-embedding-3-small`) or Ollama locally to get a floating-point vector.
2. `cosine_similarity(v1, v2)`:
```python
# Manual dot-product over magnitudes
import numpy as np

def cosine_similarity(a, b):
    a_arr = np.array(a)
    b_arr = np.array(b)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))

```


3. `search_code(query_str, node_embeddings_dict, top_k=5)`: Vectorizes query, computes similarity against all function embeddings, returns top matching node IDs with scores.

---

### File 6: `backend/app.py`

**Goal:** FastAPI REST API connecting graph algorithms, parsing, and search to the frontend.
**Endpoints:**

* `POST /api/scan`: Accepts `{ "repo_path": "test_repo" }`. Parses all `.py` and `.js` files, builds `networkx` graph, calculates complexity, and stores graph in memory.
* `GET /api/graph`: Returns formatted `{ nodes, edges }` JSON for the frontend graph view.
* `GET /api/blast-radius?node_id=...`: Returns array of impacted node IDs from BFS traversal.
* `GET /api/cycles`: Returns array of circular dependency loops.
* `POST /api/search`: Accepts `{ "query": "error handling" }`, runs vector search, returns top matching nodes.

---

### File 7: `frontend/src/App.jsx` & Components

**Goal:** Clean, dark-mode, single-page React dashboard with an interactive node graph and detail drawer.
**Components:**

1. `App.jsx`: State management for selected node, search results, highlighted blast radius nodes, and active tab.
2. `GraphView.jsx`: Interactive graph canvas using SVG/HTML Canvas or `@xyflow/react` / `vis-network`. Nodes colored by type (Function = Orange, Class = Green, Module = Blue). Clicking a node triggers selection callback.
3. `DetailPanel.jsx`: Side drawer showing:
* Selected node name, type, and file location.
* Code snippet with syntax highlighting.
* Cyclomatic Complexity score badge.
* "Calculate Blast Radius" button (highlights impacted caller nodes in Red).


4. `SearchBar.jsx`: Input box to trigger semantic search and jump to relevant code nodes.

---

## 5. GENERATION PROTOCOL

When generating files:

1. Start with `backend/requirements.txt`, then build `parser_engine.py`, `complexity.py`, `graph_builder.py`, `vector_search.py`, and `app.py`.
2. Generate `test_repo/` sample files so the server can be tested immediately.
3. Create frontend package files and React components.
4. Ensure all code is functional, imports match, and the code style remains student-written (no fluff, clear logic, sparse informal comments).

```

***

### How to use this file:

1. Create a new project folder named `code-kg`.
2. Create a file named `PROJECT_BUILDER.md` inside `code-kg/` and paste the text above into it.
3. Open **Cursor**, **Windsurf**, or **Claude Dev** in `code-kg/`.
4. Run this prompt in your AI agent:
   > *"Read `PROJECT_BUILDER.md` completely. Follow all instructions and persona rules. Generate the full, complete codebase skeleton for all files listed in section 3. Write real, working Python and React code for every file without using placeholders or skipping logic."*

This will give you a fully functional, complete codebase that looks clean, organic, and student-built—ready for you to review and master line-by-line for your interview!

```