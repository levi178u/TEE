# import ast
# from pathlib import Path

# def parse_python_file(file_path):
#     with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#         source = f.read()
#     tree = ast.parse(source)
#     nodes = []
#     for node in ast.walk(tree):
#         if isinstance(node, ast.FunctionDef):
#             nodes.append({
#                 "type": "function",
#                 "name": node.name,
#                 "lineno": node.lineno,
#                 "end_lineno": getattr(node, "end_lineno", None)
#             })
#         elif isinstance(node, ast.ClassDef):

#             nodes.append({
#                 "type": "class",
#                 "name": node.name,
#                 "lineno": node.lineno,
#                 "end_lineno": getattr(node, "end_lineno", None)
#             })
#     return nodes