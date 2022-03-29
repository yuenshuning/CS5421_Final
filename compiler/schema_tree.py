from typing import Dict, List, Optional
import pymongo
from pymongo.collection import Collection


class SchemaNode:
    def __init__(self, name: str = '', parent=None, children=[]):
        self.name = name
        self.parent = parent  # type: SchemaNode
        self.children = children  # type: List[SchemaNode]

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
            res = func(node, name)
            if len(res) > 0:
                new_nodes.extend(res)
        return new_nodes

    def _ancestor(self, node: SchemaNode, name):
        new_nodes = []
        if node.parent is None:
            return new_nodes
        if name == '*' or node.parent.name == name:
            new_nodes.append(node.parent)
        ret = self._ancestor(node.parent, name)
        if len(ret) > 0:
            new_nodes.extend(ret)
        return new_nodes

    def _ancestor_or_self(self, node: SchemaNode, name):
        new_nodes = self._ancestor(node, name)
        if name == '*' or node.name == name:
            new_nodes.append(node)
        return new_nodes

    def _child(self, node: SchemaNode, name):
        new_nodes = []
        for child in node.children:
            if name == '*' or child.name == name:
                new_nodes.append(child)
        return new_nodes

    def _descendant(self, node: SchemaNode, name):
        new_nodes = []
        for child in node.children:
            if name == '*' or child.name == name:
                new_nodes.append(child)
            ret = self._descendant(child, name)
            if len(ret) > 0:
                new_nodes.extend(ret)
        return new_nodes

    def _descendant_or_self(self, node: SchemaNode, name):
        new_nodes = self._descendant(node, name)
        if name == '*' or node.name == name:
            new_nodes.append(node)
        return new_nodes

    def _following(self, node: SchemaNode, name):
        new_nodes = []
        cur = node
        parent = cur.parent
        while parent is not None:
            is_following = False
            for child in parent.children:
                if is_following:
                    new_nodes.extend(self._descendant_or_self(node, name))
                if child == cur:
                    is_following = True
            cur = parent
            parent = cur.parent
        return new_nodes

    def _following_sibling(self, node: SchemaNode, name):
        new_nodes = []
        parent = node.parent
        if parent is None:
            return new_nodes
        is_following = False
        for child in parent.children:
            if is_following:
                if name == '*' or child.name == name:
                    new_nodes.append(child)
            if child == node:
                is_following = True
        return new_nodes

    def _namespace(self, node: SchemaNode, name):
        pass

    def _parent(self, node: SchemaNode, name):
        if node.parent is not None and (name == '*' or node.parent.name == name):
            return [node.parent]
        return []

    def _preceding(self, node: SchemaNode, name):
        new_nodes = []
        cur = node
        parent = cur.parent
        while parent is not None:
            for child in parent.children:
                if child == cur:
                    break
                new_nodes.extend(self._descendant_or_self(node, name))
            cur = parent
            parent = cur.parent
        return new_nodes

    def _preceding_sibling(self, node: SchemaNode, name):
        new_nodes = []
        parent = node.parent
        if parent is None:
            return new_nodes
        for child in parent.children:
            if child == node:
                break
            if name == '*' or child.name == name:
                new_nodes.append(child)
        return new_nodes

    def _self(self, node: SchemaNode, name):
        if name == '*' or node.name == name:
            return [node]
        return []


if __name__ == '__main__':
    from mongodb_helper import db_connect

    db = db_connect()
    col = db['library']
    tree = SchemaTree(col)
    tree.print_tree()
