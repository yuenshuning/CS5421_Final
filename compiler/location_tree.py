from typing import List
from .schema_tree import SchemaTree, SchemaNode


class LocationNode:
    def __init__(self):
        self.steps = []

    def add_step(self, axis='child', name='', predicates=[]):
        self.steps.append((axis, name, predicates))

    def generate(self, schema_tree: SchemaTree, schema_nodes: List[SchemaNode], is_top=False):
        ret = []
        for axis, name, predicates in self.steps:
            if name != '__root__':
                schema_nodes = schema_tree.find(schema_nodes, axis, name)
            for pr in predicates:
                ret.append({
                    '$match': pr.generate(schema_tree, schema_nodes)
                })
        if is_top:
            project_dict = {}
            for node in schema_nodes:
                name = node.name
                if name not in project_dict:
                    project_dict[name] = []
                project_dict[name].append('$' + str(node))
            ret.append({
                '$project': {
                    '_id': 0,
                    **{k: v for k, v in project_dict.items()}
                }
            })
        return ret, schema_nodes
