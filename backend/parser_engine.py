import os
import re
from typing import Dict, List

try:
    import tree_sitter_languages as tsl
except Exception:  # pragma: no cover
    tsl = None

try:
    from tree_sitter import Parser
except Exception:  # pragma: no cover
    Parser = None


def _get_parser(language_name: str):
    if Parser is None or tsl is None:
        return None

    try:
        if language_name == "python":
            lang = tsl.get_language("python")
        else:
            lang = tsl.get_language("javascript")
    except Exception:
        return None

    parser = Parser()
    parser.set_language(lang)
    return parser


def _get_node_name(node, lang_name: str):
    if node is None:
        return ""

    for child in node.children:
        if child.type in {"identifier", "name", "property_identifier"}:
            return child.text.decode("utf-8", errors="ignore")

    if hasattr(node, "child_by_field_name"):
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            return name_node.text.decode("utf-8", errors="ignore")

    return ""


def _extract_import_names(node):
    names = []
    for child in node.children:
        if child.type in {"identifier", "dotted_name", "aliased_import"}:
            text = child.text.decode("utf-8", errors="ignore")
            if text:
                names.append(text)
    return names


def _collect_calls(node, lang_name: str, out_list: List[Dict]):
    if node is None:
        return

    node_type = node.type
    if node_type in {"call", "call_expression"}:
        name = ""
        if node.children:
            first = node.children[0]
            name = first.text.decode("utf-8", errors="ignore")
            if name == "" and hasattr(first, "type") and first.type == "member_expression":
                name = first.children[-1].text.decode("utf-8", errors="ignore")
        if name:
            out_list.append({"name": name})

    for child in node.children:
        _collect_calls(child, lang_name, out_list)


def parse_file(file_path: str) -> Dict:
    abs_path = os.path.abspath(file_path)
    with open(abs_path, "rb") as handle:
        raw_bytes = handle.read()

    text = raw_bytes.decode("utf-8", errors="ignore")
    ext = os.path.splitext(abs_path)[1].lower()
    if ext == ".py":
        language_name = "python"
    elif ext == ".js":
        language_name = "javascript"
    else:
        language_name = "text"

    parser = _get_parser(language_name)
    tree = None
    if parser is not None:
        try:
            parser.reset()
            parser.feed(raw_bytes)
            tree = parser.finish()
        except Exception:
            tree = None

    functions = []
    classes = []
    imports = []
    calls = []

    if tree is not None:
        root = tree.root_node

        def walk(node):
            node_type = node.type
            if language_name == "python" and node_type == "function_definition":
                name = _get_node_name(node, language_name)
                if name:
                    functions.append({"name": name, "code": node.text.decode("utf-8", errors="ignore")})
            elif language_name == "javascript" and node_type in {"function_declaration", "arrow_function"}:
                name = _get_node_name(node, language_name)
                if name:
                    functions.append({"name": name, "code": node.text.decode("utf-8", errors="ignore")})
            elif language_name == "python" and node_type == "class_definition":
                name = _get_node_name(node, language_name)
                if name:
                    classes.append({"name": name, "code": node.text.decode("utf-8", errors="ignore")})
            elif language_name == "javascript" and node_type == "class_declaration":
                name = _get_node_name(node, language_name)
                if name:
                    classes.append({"name": name, "code": node.text.decode("utf-8", errors="ignore")})
            elif node_type in {"import_statement", "import_from_statement"}:
                import_names = _extract_import_names(node)
                if import_names:
                    imports.append({"name": ", ".join(import_names)})
            elif node_type in {"call", "call_expression"}:
                name = ""
                if node.children:
                    first = node.children[0]
                    name = first.text.decode("utf-8", errors="ignore")
                    if name == "" and hasattr(first, "type") and first.type == "member_expression":
                        name = first.children[-1].text.decode("utf-8", errors="ignore")
                if name:
                    calls.append({"name": name})

            for child in node.children:
                walk(child)

        walk(root)

    if not functions and not classes and not imports and not calls:
        # fallback for simple local testing when tree-sitter is not ready
        for match in re.finditer(r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
            functions.append({"name": match.group(1), "code": ""})
        for match in re.finditer(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", text):
            classes.append({"name": match.group(1), "code": ""})
        for match in re.finditer(r"import\s+([A-Za-z0-9_.]+)", text):
            imports.append({"name": match.group(1)})
        for match in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
            if match.group(1) not in {"def", "if", "for", "while", "return", "class", "import"}:
                calls.append({"name": match.group(1)})

    return {
        "file_path": abs_path,
        "language": language_name,
        "code": text,
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "calls": calls,
    }
