
from abstract import MetaContainer, MetaDecoder, MetaEncoder


class _Register:
    def __init__(self):
        self.container_dict = {}
        self.parse_dict = {}

    def register(self, inclass=None, outclass=None):
        def register_decorator(_class):
            if not isinstance(_class, type): _class = type(_class)
            if issubclass(_class, MetaEncoder):
                assert inclass is not None and outclass is not None, 'input & output class must be specified for encoder'
                self._add_to_dict(self.parse_dict, (inclass, outclass), _class)
            elif issubclass(_class, MetaDecoder):
                assert inclass is not None and outclass is not None, 'input & output class must be specified for decoder'
                self._add_to_dict(self.parse_dict, (inclass, outclass), _class)
            elif issubclass(_class, MetaContainer):
                self._add_to_dict(self.container_dict, _class, _class)
            else:
                print(f'unrecognized class regitry {_class}, maybe you should inherit from abstract classes')
            return _class
        return register_decorator

    def _add_to_dict(self, d, key, value):
        if key in d:
            print(f'{key} has already in the dictionary, may cause conflict')
        d[key] = value


    def provide_parser(self, inclass, outclass):
        if not isinstance(inclass, type): inclass = type(inclass)
        if not isinstance(outclass, type): outclass = type(outclass)

        return self.parse_dict.get((inclass, outclass), MetaEncoder)

    def provide_container(self, inclass):
        if not isinstance(inclass, type): inclass = type(inclass)
        return self.container_dict.get(inclass, MetaContainer)
        


Register = _Register()
