import difflib
import time
from copy import deepcopy
from pathlib import Path

import MutationOp, MantraOperators
from pyverilog.vparser.parser import parse, NodeNumbering
import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import sys, inspect, subprocess
import os, random
from optparse import OptionParser
from random import randint
 

class ASTCollector:
    def __init__(self):
        self.node_dict = {}
        self.u_ops = set()
        self.ops = set()
        self.const = set()

    def visit(self, ast):
        for child in ast.children():
            if child is not None:
                self.node_dict[child.node_id] = child.__class__.__name__
                if isinstance(child, vast.UnaryOperator):
                    self.u_ops.add(child.__class__)
                elif isinstance(child, vast.Operator):
                    self.ops.add(child.__class__)
                elif isinstance(child, vast.Constant):
                    self.const.add(child)
                self.visit(child)


def visit_children_attr(ast):
    for child in ast.children():
        if child is not None:
            # Save the child's name and id to the dictionary
            print(vars(child))
            visit_children_attr(child)


def diff_file(text1: str, text2: str):
    diff = difflib.unified_diff(text1.splitlines(), text2.splitlines())
    res = '\n'.join(list(diff))
    return res

def gen_mutation(file_name: str,n: int, max_n: int, out_path: Path):
    if not out_path.exists():
        out_path.mkdir(parents=True, exist_ok=True)

    ast, directives = parse([file_name])
    mantra_operator = MantraOperators.MantraOperators(None, None, None)
    cu = ASTCollector()
    cu.visit(ast)

    mod_pos = []
    for key, value in cu.node_dict.items():
        if value in ['BlockingSubstitution', 'Assign', 'NonblockingSubstitution']:
            mod_pos.append(key)

    codegen = ASTCodeGenerator()
    origin_code = codegen.visit(ast)
    with open(out_path / f'origin_{file_name}', 'w') as f:
        f.write(origin_code)

    max_cnt = min(len(mod_pos), max_n)
    for ii in range(n):
        cpy_ast = deepcopy(ast)

        pos = random.sample(mod_pos, max_cnt)

        for key, value in cu.node_dict.items():
            if key in pos:
                cpy_ast = mantra_operator.SME_operator(cpy_ast, key, list(cu.u_ops), list(cu.ops), list(cu.const))

        src_code = codegen.visit(cpy_ast)

        with open(out_path / f'mut_{ii}_{file_name}', 'w') as f:
            f.write(src_code)
        with open(out_path / f'mut_{ii}_{file_name}.diff', 'w') as f:
            f.write(diff_file(origin_code, src_code))

if __name__ == "__main__":
    file_name = "xlnxstream_2018_3.v"

    gen_mutation(file_name, 10, 1, Path("wk_dir"))
