from typing import List, Dict
from lark import Tree
from lark.lexer import Token
from sympy import E

from .location_tree import LocationNode
from .schema_tree import SchemaTree, SchemaNode

class PredicateNodeType:
    constant = 1
    expression = 2
    variable = 3
    function = 4


class PredicateNode:
    def __init__(self, lhs, op, rhs, **kwargs):
        self._type_recognize(op, **kwargs)
        self.lc = self.convert(lhs)
        self.rc = self.convert(rhs)
        self.tree = None # type: PredicateTree

    def _type_recognize(self, op, **kwargs):
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
            elif op.type == 'FUNCTION_NAME':
                self.op = op.value
                self.type = PredicateNodeType.function
                self.args = kwargs['args']
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
        # leaf node
        if self.type == PredicateNodeType.constant:
            return self.op
        elif self.type == PredicateNodeType.variable:
            _, schema_nodes = self.op.generate(schema_tree, schema_nodes) # TODO: nested predicate, now we only use the node
            return _, schema_nodes
        elif self.type == PredicateNodeType.function:
            if self.op == 'count':
                _, schema_nodes = self.args[0].generate(schema_tree, schema_nodes)
                extra_names = []
                for n in schema_nodes:
                    extra_name = f'__count_{str(n).replace(".", "_")}__'
                    extra_names.append(extra_name)
                    self.tree.extra_set_fields[extra_name] = {
                        '$cond': {
                            'if': {
                                '$isArray': '$' + str(n)
                            },
                            'then': {
                                '$size': '$' + str(n)
                            },
                            'else': 1
                        }
                    } 
                return extra_names

        # non-leaf node
        if self.op == '>=':
            if self.lc.type == PredicateNodeType.variable and self.rc.type == PredicateNodeType.constant:
                _, schema_nodes = self.lc.generate(schema_tree, schema_nodes)
                rc_gen = self.rc.generate(schema_tree, schema_nodes)
                match = {str(n): {'$gte': rc_gen} for n in schema_nodes}
                return match
        elif self.op == '<=':
            if self.lc.type == PredicateNodeType.variable and self.rc.type == PredicateNodeType.constant:
                _, schema_nodes = self.lc.generate(schema_tree, schema_nodes)
                rc_gen = self.rc.generate(schema_tree, schema_nodes)
                match = {str(n): {'$lte': rc_gen} for n in schema_nodes}
                return match
            if self.lc.type == PredicateNodeType.function and self.rc.type == PredicateNodeType.constant:
                extra_names = self.lc.generate(schema_tree, schema_nodes)
                rc_gen = self.rc.generate(schema_tree, schema_nodes)
                match = {e: {'$lte': rc_gen} for e in extra_names}
                return match
        elif self.op == 'and':
            if self.lc.type == PredicateNodeType.expression and self.rc.type == PredicateNodeType.expression:
                lc_gen = self.lc.generate(schema_tree, schema_nodes)
                rc_gen = self.rc.generate(schema_tree, schema_nodes)
                return {'$and': [lc_gen, rc_gen]}
        else:
            raise RuntimeError()

class PredicateTree:
    def __init__(self, root_node: PredicateNode):
        self.root = root_node
        self.extra_set_fields = {}
        PredicateTree.recursive_register_tree(self, self.root)

    @staticmethod
    def recursive_register_tree(tree, node: PredicateNode):
        if node is None: return
        node.tree = tree
        PredicateTree.recursive_register_tree(tree, node.lc)
        PredicateTree.recursive_register_tree(tree, node.rc)

    def generate(self, schema_tree: SchemaTree, schema_nodes: List[SchemaNode]):
        self.extra_set_fields = {}
        match_result = self.root.generate(schema_tree, schema_nodes)
        if len(self.extra_set_fields):
            return [
                {'$addFields': self.extra_set_fields},
                {'$match': match_result},
                {'$project': {k: 0 for k in self.extra_set_fields.keys()}}
            ]
        else:
            return [{'$match': match_result}]
