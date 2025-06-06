import ast
import marshal

from typing import Any, Dict, List

from src.analyzer2.global_visitor import GlobalVisitor


class SourceAnalyzer:
    def __init__(self, code: bytes) -> None:
        self.code: bytes = code
        self.tree: ast.Module = ast.parse(self.code)
        self.visitor = GlobalVisitor(code)
        self.visitor.visit(self.tree)
        self.__globals: Dict[str, Any] = []

    def extract_exec_calls(self, func_name: str = "exec") -> List[ast.Call]:
        exec_calls = []

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == func_name:
                exec_calls.append(node)

        return exec_calls

    def extract_exec_calls_with_body(self, func_name: str = "exec") -> List:
        return [ast.get_source_segment(self.code.decode(), exec_call) for exec_call in self.extract_exec_calls(func_name=func_name)]

    @property
    def globals(self) -> Dict[str, Any]:
        # exec key's values to get thire values
        # and return as map {'s' = 38, ...}
        if self.__globals:
            return self.__globals
        deleted_defs_keies = []
        for key, body in self.visitor.defs.items():
            try:
                exec(
                    compile(
                        ast.Module(
                            body=[body],
                            type_ignores=[]
                        ), "defs", "exec"
                    ),
                     {}, globals())
            except Exception as e:
                deleted_defs_keies.append(key)

        for key in self.visitor.defs.keys():
            if not key in deleted_defs_keies:
                self.visitor.global_vars[key] = eval(key)
        
        self.__globals = self.visitor.global_vars
        return self.__globals


    def get_bytecodes(self) -> List[bytes]:
        # this function get marshall bytecode like [b'\x1b...', ...]
        bytecodes: List[bytes] = []
        for i in ast.walk(self.tree):
            if isinstance(i, ast.Call) and isinstance(i.func, ast.Attribute) and isinstance(i.func.value, ast.Name):
                if self.globals.get(i.func.value.id) is marshal and i.func.attr == "loads":
                    try:
                        body = ast.get_source_segment(self.code.decode(), i.args[0])
                        bytecodes.append(eval(body, {}, self.globals))
                    except Exception as e:
                        print("ERROR in get_bytecodes", e)
        return bytecodes

    def try_to_get_exec_restults(self, id: str = 'exec') -> List[Any]:
        # this function try to run all exec bodies that found in file
        # the output will be like [codeObject, ...], ["import mar...", ....] or [b'import ...', ...] or []
        results: List[Any] = []
        self.globals
        self.__globals[id] = lambda compiled, *args, **kwargs: compiled
        for i in ast.walk(self.tree):
            if isinstance(i, ast.Call) and isinstance(i.func, ast.Name) and i.func.id == id:
                body = ast.get_source_segment(self.code.decode(), i)
                try:
                    results.append(eval(body, {}, self.__globals))
                except Exception as e:
                    print("marshal:", e)
                    pass
        self.__globals.pop(id)
        return results
