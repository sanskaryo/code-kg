import os
import sys
from pathlib import Path

# Add parent directory to sys.path to import backend modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.parser_engine import parse_file


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "backend/test_repo"
    print(f"--- Parsing JavaScript files in '{target_dir}' ---")

    js_files = []
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith((".js", ".jsx", ".ts", ".tsx")):
                js_files.append(os.path.join(root, file))

    if not js_files:
        print("No JavaScript (.js, .jsx, .ts, .tsx) files found.")
        return

    all_parsed = []
    for filepath in js_files:
        parsed = parse_file(filepath)
        all_parsed.append(parsed)
        print(f"\n[File] {filepath}")
        print(f"  • Functions ({len(parsed['functions'])}): {[f['name'] for f in parsed['functions']]}")
        print(f"  • Classes ({len(parsed['classes'])}): {[c['name'] for c in parsed['classes']]}")
        print(f"  • Imports ({len(parsed['imports'])}): {[i['name'] for i in parsed['imports']]}")
        print(f"  • Calls ({len(parsed['calls'])}): {[c['name'] for c in parsed['calls']]}")

    print(f"\nTotal JavaScript files parsed: {len(all_parsed)}")


if __name__ == "__main__":
    main()
