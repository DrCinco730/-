import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Marshal-Magic is a command-line tool that decodes and deobfuscates any Python file, regardless of its version. It's fast, easy-to-use, and perfect for decoding even the most complex obfuscated code.")
    parser.add_argument('filename', type=str,
                        help='input file path that you whant to decode', metavar="file.py")
    parser.add_argument('-o', '--output', type=str,
                        help='output file path to save the decoded file in', metavar="out_file.py")
    parser.add_argument('-m', '--mode', type=str,
                        help='select a mode to set the decoding algorithm.', default="simple", metavar="<mode>")
    parser.add_argument('-v', '--version', type=str,
                        help='specify a Python version for loading a compiled code object', default="3.9", metavar="<x.y>")

    return parser.parse_args()
