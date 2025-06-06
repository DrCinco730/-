import os

from typing import Any, Union, Iterable

from src.analyzer2.source_analyzer import SourceAnalyzer


TEST_FILES_PATH: str = "C:/Users/MSI/Downloads/Telegram Desktop"

class TestSourceAnalyzer:
    def __init__(self,  files: list) -> None:
        self.success_get_globals: int = 0
        self.success_get_bytecode: int = 0
        self.success_try_get_results: int = 0
        self.total_files: int = 0
        self.files: list = files

    def get_source_analyser(self, code: bytes) -> Union[SourceAnalyzer, None]:
        try:
            compile(code, "", "exec")
        except Exception as e:
            print(e)
        else:
            return SourceAnalyzer(code)

    def walk_py_files(self) -> Iterable[str]: 
        for file in self.files:
            if file.endswith(".py"):
                yield os.path.join(TEST_FILES_PATH, file)

    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def get_features(self, source_analyzer: SourceAnalyzer) -> list:
        return [source_analyzer.globals, source_analyzer.get_bytecodes(), source_analyzer.try_to_get_exec_restults()]

    def print(self, name: str, data: Any) -> None:
        data: str = f"{data[:100]}...{len(data)-130}...{data[-20:]}" if len(
            data := str(data)) > 120 else str(data)
        print(f"\x1b[0m{name}:", data)

    def update_values(self, g, b, r) -> None:
        if g: self.success_get_globals += 1
        if b: self.success_get_bytecode += 1
        if r: self.success_try_get_results += 1
        return [g, b, r]

    def percent(self, p: int) -> str:
        return f"{p} from {self.total_files}   ->  \x1b[34m{round(p / self.total_files * 100)}%\x1b[0m"

    def print_final_info(self) -> None:
        self.print(f"success get globals", self.percent(self.success_get_globals))
        self.print(f"success get bytecodes", self.percent(self.success_get_bytecode))
        self.print(f"success try get results", self.percent(self.success_try_get_results))

    def analise(self) -> None:
        for pyfile in self.walk_py_files():
            self.total_files += 1
            code: bytes = self.read(pyfile)
            print('\x1b[34m', pyfile, "\x1b[0m")
            source_analyzer: SourceAnalyzer = self.get_source_analyser(code)
            if source_analyzer:
                _globals, _bytecodes, _get_results = self.update_values(*self.get_features(source_analyzer))
                self.print("globals", _globals)
                self.print("marshal bytecodes", _bytecodes)
                self.print("try get exec results", _get_results)
                
            else:
                self.print("# error", "the file has errors")
            print("\n\n")
        self.print_final_info()



def test() -> None:
    test = TestSourceAnalyzer(os.listdir(TEST_FILES_PATH))
    test.analise()


if __name__ == "__main__":
    test()




# a = importlib._bootstrap_external._code_to_timestamp_pyc(a)
# with open("te.pyc", "wb") as f:
#     f.write(a)