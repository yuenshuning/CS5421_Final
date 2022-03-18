from abstract import MetaEncoder
from ..container import BasicContainer
from register import Register

@Register.register(inclass=str, outclass=BasicContainer)
class BasicEncoder(MetaEncoder):
    def __init__(self, *arg, **kwargs):
        pass

    def encode(self, xpath: str, *args, **kwargs):
        container = Register.provide_container(BasicContainer)(xpath) # type: BasicContainer
        return container
