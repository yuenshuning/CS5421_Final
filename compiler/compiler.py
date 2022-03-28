from lark import Lark
if __package__:
    from .evaluator import XpathEvaluator1
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
        pass

    def solve(self, expr):
        return expr

if __name__ == '__main__':
    test_parse()
