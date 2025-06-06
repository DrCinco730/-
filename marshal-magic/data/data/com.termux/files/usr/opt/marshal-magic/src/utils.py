import autopep8

from typing import Union
from types import CodeType
from dis import dis

from rich.console import Console
from rich.syntax import Syntax

console = Console()

def fix_code_and_save(source_code: str, args):
    if isinstance(source_code, str):
        file_path = args.output
        if file_path == "==":
            file_path = args.filename
        with open(file_path, "w") as f:
            f.write("# Decoded by marshal-magic\n")
            f.write("# Follow us on telegram @psh_team\n")
            f.write(autopep8.fix_code(source_code))
    else:
        console.print("Can't save %s" % source_code)
        exit(1)


def fix_code_and_print(source_code: str):
    if isinstance(source_code, str):
        source_code = autopep8.fix_code(source_code)
        console.print("# Decoded by marshal-magic")
        console.print("# Follow us on telegram @psh_team")
        if len(source_code) < 30000:
            syntax = Syntax(source_code, 'python', line_numbers=True)
            console.print(syntax)
        else:
            print(source_code)
    else:
        console.print("Can't print %s" % source_code)
        exit(1)


def safe_check(bytecode: CodeType):
    co_consts_status = list(
        map(lambda e: e in bytecode.co_consts, (False, 1, 0)))
    co_names_status = list(
        map(lambda e: e in bytecode.co_names, ("foo", "bar")))

    return all(co_names_status+co_consts_status)
