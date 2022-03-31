from lark import Transformer, Tree
from lark.lexer import Token

if __package__:
    from .schema_tree import SchemaTree
    from .predicate_tree import PredicateNode, PredicateTree
    from .location_tree import LocationNode
else:
    from schema_tree import SchemaTree
    from predicate_tree import PredicateNode, PredicateTree
    from location_tree import LocationNode


class XpathEvaluator1(Transformer):
    def __init__(self, tree: SchemaTree):
        super(Transformer, self).__init__()
        self.tree = tree
        self.pipeline_command = []

    def additive_expr(self, parts):
        pass

    def location_path(self, parts):
        node = LocationNode()
        i = 0
        while i < len(parts):
            part = parts[i]
            axis = 'child'
            if isinstance(part, Token) and part.type in {'SLASH', 'DOUBLE_SLASH'}:
                axis = 'child' if part.type == 'SLASH' else 'descendant'
                i += 1
            step = parts[i]  # type: Tree
            for j, child in enumerate(step.children):
                if child.type == 'AXIS_NAME':
                    axis = str(child.value).replace('-', '_')
                if isinstance(child, Token) and child.type == 'NAME_TEST':
                    name = child.value  # type: str
                    node.add_step(axis=axis, name=name, predicates=step.children[j + 1:])
                    break
            i += 1
        return node

    def and_expr(self, parts):
        lhs, op, rhs = parts
        ret = PredicateNode(lhs, op, rhs)
        return ret

    def relational_expr(self, parts):
        lhs, op, rhs = parts
        ret = PredicateNode(lhs, op, rhs)
        return ret

    def predicate(self, parts):
        assert len(parts) == 1
        return PredicateTree(parts[0])

    def function_call(self, parts):
        name, args = parts[0], parts[1].children
        return PredicateNode(None, name, None, args=args)
