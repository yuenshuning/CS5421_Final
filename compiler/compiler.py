from lark import Lark
import json

if __package__:
    from .evaluator import XpathEvaluator1
    from .mongodb_helper import db_connect
    from .schema_tree import SchemaTree
    from .location_tree import LocationNode
else:
    from evaluator import XpathEvaluator1
    from mongodb_helper import db_connect
    from schema_tree import SchemaTree


def test_files():
    with open('compiler/xpath1.lark', 'r') as f:
        parser = Lark(f, start='location_path')
    tree = SchemaTree(db_connect()['test'])
    evalualtor = XpathEvaluator1(tree)

    with open('test/test.txt', 'r') as f:
        for row in f.readlines():
            if row.startswith('/'):
                try:
                    print(row)
                    res = parser.parse(row)
                    print(res.pretty())
                    evalualtor.transform(res)
                except Exception as e:
                    print(e)

def test_parse():
    with open('compiler/xpath1.lark', 'r') as f:
        parser = Lark(f, start='location_path')
    xpath = '/hobbies/indoor'
    col = db_connect()['library']
    tree = SchemaTree(col)
    tree.print_tree()
    evalualtor = XpathEvaluator1(tree)
    res = parser.parse(xpath)
    evalualtor.transform(res)
    res = col.aggregate(evalualtor.pipeline_command)
    for c in res:
        print(c)

class Solver:
    def __init__(self, config):
        self.config = config
        self.colllection = db_connect(config['URI'], config['DATABASE'])[config['COLLECTION']]
        self.tree = SchemaTree(self.colllection)
        # self.tree.print_tree()
        with open('compiler/xpath1.lark', 'r') as f:
            self.parser = Lark(f, start='location_path')
        self.evaluator = XpathEvaluator1(self.tree)

    def solve(self, expr):
        expr = expr.replace('/child::{}/child::{}'.format(self.config['COLLECTION'], self.config['COLLECTION_ITEM']), '/__root__')
        res = self.parser.parse(expr)
        # print(res.pretty())
        node = self.evaluator.transform(res) # type: LocationNode
        aggs, _ = node.generate(self.tree, [self.tree.root], is_top=True)
        res = self.colllection.aggregate(aggs)

        ret = []
        for obj in res:
            for k, v in obj.items(): # assume there would be only one k-v pair
                if isinstance(v, list):
                    ret += [{k: item} for item in v]
                else:
                    ret.append({k: v})
        ret = [json.dumps(r) for r in ret]
        return ret


if __name__ == '__main__':
    pass
