from importlib.resources import path
from platform import node
from lark import Transformer, Tree
from lark.lexer import Token
from torch import isin
if __package__:
    from .schema_tree import SchemaTree
else:
    from schema_tree import SchemaTree

class XpathEvaluator1(Transformer):
    def __init__(self, tree: SchemaTree):
        super(Transformer, self).__init__()
        self.tree = tree
        self.pipeline_command = []

    def additive_expr(self, parts):
        print(parts)

    def location_path(self, parts):
        i = 0
        nodes = [self.tree.root]
        while i < len(parts):
            part = parts[i]
            if isinstance(part, Token) and part.type in {'SLASH', 'DOUBLE_SLASH'}:
                print(nodes)
                relation = part
                i += 1
                part = parts[i] # type: Tree
                for child in part.children:
                    if isinstance(child, Token) and child.type == 'NAME_TEST':
                        name = child.value # type: str
                        nodes = self.tree.find(nodes, relation.type, name)
                        self.pipeline_command.append({
                            '$project': {str(node): 1 for node in nodes}
                        })
                        break
            i += 1
        print(nodes)
