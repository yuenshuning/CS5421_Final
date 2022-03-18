from abstract import MetaContainer
from register import Register

@Register.register()
class PathContainer(MetaContainer):
    def __init__(self, path, index, *args, **kwargs):
        self.path = path
        self.index = index