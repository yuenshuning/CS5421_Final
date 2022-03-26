from email import parser
from lark import Lark

if __name__ == '__main__':
    xpath = '/bookstore/book[last()]'
    with open('compiler/xpath1.lark', 'r') as f:
        parser = Lark(f, start='location_path')
    res = parser.parse(xpath)
    print(res.pretty())
