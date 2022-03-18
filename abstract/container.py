from abc import ABC, abstractmethod


class MetaContainer(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs): pass
