from abc import ABC, abstractmethod
from .container import MetaContainer


class MetaEncoder(ABC):
    @abstractmethod
    def __init__(self, *arg, **kwargs): pass

    @abstractmethod
    def encode(self, incontainer: MetaContainer, *args, **kwargs): pass
