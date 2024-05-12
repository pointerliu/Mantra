import MutationOp, MantraOperators
from pyverilog.vparser.parser import parse, NodeNumbering
import pyverilog.vparser.ast as vast
from pyverilog.ast_code_generator.codegen import ASTCodeGenerator
import sys, inspect, subprocess
import os, random
from optparse import OptionParser
from random import randint
 

def visit_children(ast, node_dict=None, u_ops=None, ops=None):
    if node_dict is None:
        node_dict = {}
    if u_ops is None:
        u_ops = set()
    if ops is None:
        ops = set()
    if ast is None:
        return node_dict
    for child in ast.children():
        if child is not None:
            # Save the child's name and id to the dictionary
            node_dict[child.node_id] = child.__class__.__name__
            if child.__class__.__name__ == 'Lor':
                _a = 1
            if isinstance(child, vast.UnaryOperator):
                u_ops.add(child.__class__)
            elif isinstance(child, vast.Operator):
                ops.add(child.__class__)
            visit_children(child, node_dict, u_ops, ops)
    return node_dict, u_ops, ops


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

    max_cnt = 1
    for key, value in nodeid_name_dict.items():
        if value == 'Assign':
            if random.random() > 0.5:
                ast = mantra_operator.SME_operator(ast, key, list(u_ops), list(ops))
                max_cnt -= 1
                if max_cnt == 0:
                    break

    # ast.show()
    # new_ast = mantra_operator.DMO(ast, pointer_id, vast.IntConst(randint(1,100)))
    # new_ast = mantra_operator.SME_constant(ast, if_id)
    codegen = ASTCodeGenerator()
    src_code = codegen.visit(ast)

    with open(f'mut_{file_name}', 'w') as f:
        f.write(src_code)
    print(src_code)
