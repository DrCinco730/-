import ast
import builtins
import sys
from typing import Any, Dict


class GlobalVisitor(ast.NodeVisitor):
    def __init__(self, code: bytes, *args, **kwargs) -> None:
        self.code: bytes = code
        self.global_vars: Dict[str, Any] = {}
        self.defs: Dict[str, Any] = {}
        super().__init__(*args, **kwargs)

    def visit_Assign(self, node: ast.Assign) -> None:
        # catch values and thire ids ...
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                try:
                    if node.value.func.id == "input": return
                except:
                    pass
                if isinstance(node.value, ast.Constant):
                    self.global_vars[node.targets[0].id] = node.value.value
                elif isinstance(node.value, ast.Call):
                    self.add_a_function_value(node, self.global_vars)
                elif isinstance(node.value, ast.Lambda):
                    self.add_a_function_value(node, self.global_vars)
               
            except Exception as e:
                print(e, "--")
        

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.global_vars[node.name] = node
        self.defs[node.name] = node

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.global_vars[node.name] = node
        self.defs[node.name] = node

    def visit_Import(self, node: ast.Import) -> None:
        for name in node.names:
            try:
                self.global_vars[name.asname or name.name] = __import__(
                    name.name, self.global_vars)
            except ModuleNotFoundError:
                pass

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        try:
            module: ast.Module = ast.Module(body=[node], type_ignores=[])
            exec(compile(module, "<string>", "exec"), {}, self.global_vars)
        except ModuleNotFoundError:
            pass

    def add_a_function_value(self, node: ast.Assign, _globals: dict = {}) -> None:
        body: str = ast.get_source_segment(self.code.decode(), node.value)
        evaled: Any = eval(body, _globals, self.global_vars)
        self.global_vars[node.targets[0].id] = evaled
    
    def visit(self, node: ast.AST) -> Any:
        # if there an input in values for example x = input(...)
        # the tool will pass x value
        stdin = sys.stdin
        sys.stdin = None
        out: Any = super().visit(node)
        sys.stdin = stdin
        return out
