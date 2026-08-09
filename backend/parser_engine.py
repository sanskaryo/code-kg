import ast
import os
import re
from typing import Dict, List


def parse_python_file(text: str) -> Dict[str, List]:
    """Parse Python code using built-in ast module."""
    functions = []
    classes = []
    imports = []
    calls = []

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {"functions": [], "classes": [], "imports": [], "calls": []}

    for node in ast.walk(tree):
        # Extract function definitions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            segment = ast.get_source_segment(text, node) or ""
            functions.append({"name": node.name, "code": segment})

        # Extract class definitions
        elif isinstance(node, ast.ClassDef):
            segment = ast.get_source_segment(text, node) or ""
            classes.append({"name": node.name, "code": segment})

        # Extract imports
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"name": alias.name})
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append({"name": f"{module}.{alias.name}" if module else alias.name})

        # Extract function calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append({"name": node.func.id})
            elif isinstance(node.func, ast.Attribute):
                calls.append({"name": node.func.attr})

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "calls": calls,
    }


def parse_js_file(text: str) -> Dict[str, List]:
    """Parse JavaScript code using clean regex patterns."""
    functions = []
    classes = []
    imports = []
    calls = []

    # Match function declaration or arrow function
    func_pattern = r"(?:function\s+([A-Za-z_][A-Za-z0-9_]*)|const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\([^)]*\)\s*=>)"
    for match in re.finditer(func_pattern, text):
        func_name = match.group(1) or match.group(2)
        if func_name:
            functions.append({"name": func_name, "code": match.group(0)})

    # Match class declaration
    for match in re.finditer(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", text):
        classes.append({"name": match.group(1), "code": match.group(0)})

    # Match import statements
    for match in re.finditer(r"import\s+.*?from\s+['\"]([^'\"]+)['\"]", text):
        imports.append({"name": match.group(1)})

    # Match function calls (excluding control structures)
    keywords = {"if", "for", "while", "switch", "catch", "return", "function", "class", "import"}
    for match in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
        name = match.group(1)
        if name not in keywords:
            calls.append({"name": name})

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "calls": calls,
    }


def parse_java_file(text: str) -> Dict[str, List]:
    """Parse Java code (Classes, Methods, Imports, Calls) using regex."""
    functions = []
    classes = []
    imports = []
    calls = []

    # Match Java class / interface / enum
    for match in re.finditer(r"(?:public|protected|private|static|\s)+class\s+([A-Za-z_][A-Za-z0-9_]*)", text):
        classes.append({"name": match.group(1), "code": match.group(0)})

    # Match Java methods
    method_pattern = r"(?:public|protected|private|static|\s)+[\w<>\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{"
    keywords = {"if", "for", "while", "switch", "catch", "class", "interface", "return"}
    for match in re.finditer(method_pattern, text):
        m_name = match.group(1)
        if m_name not in keywords:
            functions.append({"name": m_name, "code": match.group(0)})

    # Match Java imports
    for match in re.finditer(r"import\s+([A-Za-z0-9_.*]+);", text):
        imports.append({"name": match.group(1)})

    # Match Java method calls
    for match in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
        name = match.group(1)
        if name not in keywords and name not in {"System", "Math", "String", "print", "println"}:
            calls.append({"name": name})

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "calls": calls,
    }


def parse_cpp_file(text: str) -> Dict[str, List]:
    """Parse C/C++ code (Classes, Structs, Functions, Includes, Calls) using regex."""
    functions = []
    classes = []
    imports = []
    calls = []

    # Match C++ class / struct
    for match in re.finditer(r"(?:class|struct)\s+([A-Za-z_][A-Za-z0-9_]*)", text):
        classes.append({"name": match.group(1), "code": match.group(0)})

    # Match C/C++ functions
    func_pattern = r"(?:[\w:*&<>]+\s+)+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{"
    keywords = {"if", "for", "while", "switch", "catch", "return", "class", "struct", "sizeof"}
    for match in re.finditer(func_pattern, text):
        f_name = match.group(1)
        if f_name not in keywords:
            functions.append({"name": f_name, "code": match.group(0)})

    # Match #include directives
    for match in re.finditer(r"#include\s+[<\"]([^>\"]+)[>\"]", text):
        imports.append({"name": match.group(1)})

    # Match function calls
    for match in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*\(", text):
        name = match.group(1)
        if name not in keywords and name not in {"printf", "scanf", "cout", "cin"}:
            calls.append({"name": name})

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "calls": calls,
    }


def parse_file(file_path: str) -> Dict:
    """Read a file and parse code entities depending on file extension."""
    abs_path = os.path.abspath(file_path)
    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    ext = os.path.splitext(abs_path)[1].lower()
    if ext == ".py":
        parsed = parse_python_file(text)
        lang = "python"
    elif ext in {".js", ".jsx", ".ts", ".tsx"}:
        parsed = parse_js_file(text)
        lang = "javascript"
    elif ext == ".java":
        parsed = parse_java_file(text)
        lang = "java"
    elif ext in {".cpp", ".hpp", ".c", ".h", ".cc", ".cxx"}:
        parsed = parse_cpp_file(text)
        lang = "cpp"
    else:
        parsed = {"functions": [], "classes": [], "imports": [], "calls": []}
        lang = "text"

    return {
        "file_path": abs_path,
        "language": lang,
        "code": text,
        "functions": parsed["functions"],
        "classes": parsed["classes"],
        "imports": parsed["imports"],
        "calls": parsed["calls"],
    }
