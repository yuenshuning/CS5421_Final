from abstract import MetaEncoder
from ..container import BasicContainer, PathContainer
from register import Register


@Register.register(inclass=BasicContainer, outclass=PathContainer)
class PathEncoder(MetaEncoder):
    def __init__(self, *arg, **kwargs):
        pass

    def encode(self, incon: BasicContainer, *args, **kwargs):
        paths = incon.xpath.replace(' ', '')
        paths = paths.split('|')
        ret = []
        for i, path in enumerate(paths):
            con = Register.provide_container(PathContainer)(path, i)
            ret.append(con)
        return ret

