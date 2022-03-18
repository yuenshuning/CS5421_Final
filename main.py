from abstract import encoder
from xpath import BasicContainer
from register import Register
from abstract import MetaEncoder

def main():
    xpath = 'bookstore | book | b'
    encoder = Register.provide_parser(xpath, BasicContainer)() # type: MetaEncoder
    container = encoder.encode(xpath) # type: BasicContainer
    print(type(container), container.xpath)
    for path_con in container.paths:
        print(path_con.index, path_con.path)


if __name__ == '__main__':
    main()