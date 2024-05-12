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

if __name__ == "__main__":
    file_name = "xlnxstream_2018_3.v"
    ast, directives = parse([file_name])
    mutationop = MutationOp.MutationOp(None, None, None)
    mantra_operator = MantraOperators.MantraOperators(None, None, None)
    nodeid_name_dict, u_ops, ops = visit_children(ast)

    mod_pos = []
    for key, value in nodeid_name_dict.items():
        if value in ['BlockingSubstitution', 'Assign', 'NonblockingSubstitution']:
            mod_pos.append(key)

    max_cnt = min(len(mod_pos), 10)
    mod_pos = random.sample(mod_pos, max_cnt)

    for key, value in nodeid_name_dict.items():
        if key in mod_pos:
            ast = mantra_operator.SME_operator(ast, key, list(u_ops), list(ops))

    # ast.show()
    # new_ast = mantra_operator.DMO(ast, pointer_id, vast.IntConst(randint(1,100)))
    # new_ast = mantra_operator.SME_constant(ast, if_id)
    codegen = ASTCodeGenerator()
    src_code = codegen.visit(ast)

    with open(f'mut_{file_name}', 'w') as f:
        f.write(src_code)
    print(src_code)
