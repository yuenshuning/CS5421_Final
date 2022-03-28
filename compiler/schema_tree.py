from typing import Dict, List, Optional
import pymongo
from pymongo.collection import Collection

class SchemaNode:
    def __init__(self, name: str = '', parent=None, children=[]):
        self.name = name
        self.parent = parent # type: SchemaNode
        self.children = children # type: List[SchemaNode]

    def __str__(self):
        ret = self.name
        p = self.parent
        while p != None and p.parent != None:
            ret = p.name + '.' + ret
            p = p.parent
        return ret

    def __repr__(self):
        return str(self)

class SchemaTree:
    def __init__(self, col: Collection):
        self.root = SchemaNode()
        sample = col.aggregate([{'$sample': {'size': 1}}])
        sample = next(sample)
        self._build_tree(self.root, sample)

    def _build_tree(self, cur_node: SchemaNode, d: Dict):
        for k, v in d.items():
            child = SchemaNode(k, cur_node, [])
            if isinstance(v, list) and len(v):
                v = v[0]
            if isinstance(v, dict):
                self._build_tree(child, v)
            cur_node.children.append(child)

    def print_tree(self, node=None, space=0):
        if node is None:
            node = self.root
        print(' ' * space + node.name)
        for child in node.children:
            self.print_tree(child, space + 2)

    def find(self, nodes: List[SchemaNode], relation, name) -> List[SchemaNode]:
        new_nodes = []
        for node in nodes:
            func = getattr(self, '_' + relation)
            found = func(node, name)
            if found:
                new_nodes.append(found)
        return new_nodes

    def _SLASH(self, node: SchemaNode, name):
        for child in node.children:
            if child.name == name:
                return child
        return None

    def _DOUBLE_SLASH(self, node: SchemaNode, name):
        for child in node.children:
            if child.name == name:
                return child
            else:
                ret = self._DOUBLE_SLASH(child, name)
                if ret: return ret
        return None

if __name__ == '__main__':
    from mongodb_helper import db_connect
    db = db_connect()
    col = db['library']
    tree = SchemaTree(col)
    tree.print_tree()
