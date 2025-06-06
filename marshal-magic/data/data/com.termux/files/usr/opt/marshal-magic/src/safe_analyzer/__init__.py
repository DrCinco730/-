import ast
import base64
import importlib
import zlib


class SourceAnalyzer:
    def __init__(self, source_code: str) -> None:
        self.source_code = source_code
        self.exec_funcs = set()
        self.exec_libs = set()
        self.exec_body = ""

        self.eval_funcs = set()
        self.eval_libs = set()
        self.eval_body = ""

        self.loads_calls = []

        tree = ast.parse(source_code)
        exec_visitor = ExecVisitor(self)
        exec_visitor.visit(tree)

        exec_visitor = EvalVisitor(self)
        exec_visitor.visit(tree)

    def get_first_marshal_bytes(self) -> bytes:
        for arg in self.loads_calls:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, bytes):
                bytes_data = arg.value
            else:
                source_code_lines = self.source_code.split("\n")
                loads_func_lines = []
                for index, line in enumerate(source_code_lines, start=1):
                    if index >= arg.lineno and index <= arg.end_lineno:
                        loads_func_lines.append(line)

                source_code_lines.clear()

                loads_func_lines[0] = loads_func_lines[0][arg.col_offset:]
                if arg.lineno == arg.end_lineno:
                    arg.end_col_offset -=  arg.col_offset
                loads_func_lines[-1] = loads_func_lines[-1][:arg.end_col_offset]

                bytes_data = eval("\n".join(loads_func_lines))
            return bytes_data


class ExecVisitor(ast.NodeVisitor):
    def __init__(self, main_obj: SourceAnalyzer):
        self.main_obj = main_obj
        super().__init__()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'exec':
            code = node.args[0]
            self.main_obj.exec_body = ast.unparse(code)
            code_visitor = CodeVisitor(self.main_obj, func_name="exec")
            code_visitor.visit(code)            
        self.generic_visit(node)


class EvalVisitor(ast.NodeVisitor):
    def __init__(self, main_obj: SourceAnalyzer):
        self.main_obj = main_obj
        super().__init__()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == 'eval':
            code = node.args[0]
            self.main_obj.eval_body = ast.unparse(code)
            code_visitor = CodeVisitor(self.main_obj, func_name="eval")
            code_visitor.visit(code)
        self.generic_visit(node)


class CodeVisitor(ast.NodeVisitor):
    def __init__(self, main_obj : SourceAnalyzer, func_name):
        self.main_obj = main_obj
        self.func_name = func_name
        super().__init__()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            try:
                importlib.import_module(node.id)
                if self.func_name == "exec":
                    self.main_obj.exec_libs.add(node.id)
                elif self.func_name =="eval":
                    self.main_obj.eval_libs.add(node.id)
            except ImportError:
                if self.func_name == "exec":
                    self.main_obj.exec_funcs.add(node.id)
                elif self.func_name =="eval":
                    self.main_obj.eval_funcs.add(node.id)
                    
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "loads":
            # if isinstance(node.func.value, ast.Call) and isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "marshal":
                # print("found 2")
            if len(node.args) > 0:
                self.main_obj.loads_calls.append(node.args[0])
        self.generic_visit(node)

    