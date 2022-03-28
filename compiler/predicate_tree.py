from typing import List, Dict
from lark import Tree
from lark.lexer import Token

from .location_tree import LocationNode
from .schema_tree import SchemaTree, SchemaNode

class PredicateNodeType:
    constant = 1
    expression = 2
    variable = 3


class PredicateNode:
    def __init__(self, lhs, op, rhs):
        self._type_recognize(op)
        self.lc = self.convert(lhs)
        self.rc = self.convert(rhs)

    def _type_recognize(self, op):
        if isinstance(op, Token):
            if op.type == 'NUMBER':
                self.op = eval(op.value)
                self.type = PredicateNodeType.constant
            elif op.type.startswith('__ANON'):
                self.op = op.value
                self.type = PredicateNodeType.expression
            elif op.type == 'AND':
                self.op = op.value
                self.type = PredicateNodeType.expression
            else:
                raise RuntimeError()
        elif isinstance(op, LocationNode):
            self.op = op
            self.type = PredicateNodeType.variable
        else:
            raise RuntimeError()

    def convert(self, node):
        if isinstance(node, PredicateNode) or node is None:
            return node
        ret = PredicateNode(None, node, None) # leaf
        return ret

    def generate(self, schema_tree: SchemaTree, schema_nodes: List[SchemaNode]):
        if self.type == PredicateNodeType.constant:
            return self.op
        elif self.type == PredicateNodeType.variable:
            _, nodes = self.op.generate(schema_tree, schema_nodes) # TODO: nested predicate
            return [str(node) for node in nodes]

        if self.op == '>=':
            if self.lc.type == PredicateNodeType.variable and self.rc.type == PredicateNodeType.constant:
                nodes = self.lc.generate(schema_tree, schema_nodes)
                if len(nodes) == 1: # TODO: multiple result
                    return {nodes[0]: {'$gte': self.rc.generate(schema_tree, schema_nodes)}}
        elif self.op == '<=':
            if self.lc.type == PredicateNodeType.variable and self.rc.type == PredicateNodeType.constant:
                nodes = self.lc.generate(schema_tree, schema_nodes)
                if len(nodes) == 1:
                    return {nodes[0]: {'$lte': self.rc.generate(schema_tree, schema_nodes)}}
        elif self.op == 'and':
            if self.lc.type == PredicateNodeType.expression and self.rc.type == PredicateNodeType.expression:
                return {'$and': [self.lc.generate(schema_tree, schema_nodes), self.rc.generate(schema_tree, schema_nodes)]}


