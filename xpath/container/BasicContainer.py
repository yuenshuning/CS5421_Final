from abstract import MetaContainer
from register import Register
from .PathContainer import PathContainer
from typing import List

@Register.register()
class BasicContainer(MetaContainer):
    def __init__(self, xpath: str, *args, **kwargs):
        self.xpath = xpath
        self.paths = Register.provide_parser(self, PathContainer)().encode(self)