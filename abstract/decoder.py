from abc import ABC, abstractmethod


class MetaDecoder(ABC):
    @abstractmethod
    def __init__(self, *arg, **kwargs): pass

    @abstractmethod
    def decode(self, *args, **kwargs): pass
