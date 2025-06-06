import os
import sys

PREFIX = sys.prefix
EXPORT_PYTHONHOME = 'export PYTHONHOME='+PREFIX
EXECUTE_FILE = os.path.join(PREFIX,"bin/marshal-magic")
EXPORT_PYTHON_EXECUTABLE = 'export PYTHON_EXECUTABLE='+sys.executable

C_FILE = "main.c"
PYTHON_VERSION = ".".join(sys.version.split(" ")[0].split(".")[:-1])
COMPILE_FILE = (
    'gcc -I' +
    PREFIX +
    '/include/python' +
    PYTHON_VERSION +
    ' -o ' +
    EXECUTE_FILE +
    ' ' +
    C_FILE +
    ' -L' +
    PREFIX +
    '/lib -lpython' +
    PYTHON_VERSION
)
os.system(EXPORT_PYTHONHOME+" && "+EXPORT_PYTHON_EXECUTABLE+" && "+COMPILE_FILE)
os.remove(C_FILE)