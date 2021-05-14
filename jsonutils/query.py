from jsonutils.exceptions import JSONQueryException
from jsonutils.utils.dict import Defaultdict
from itertools import groupby


class Q:
    # TODO make Q object
    def __init__(self, **kwargs):

        self.AND = []
        self.OR = []
        self.NOT = []

        if len(kwargs) > 0:
            self._parse_args(kwargs)

    def _parse_args(self, kwargs):
        for k, v in kwargs.items():

            splitted = *k.split("__"), v
            self.AND.append(splitted)

    def __and__(self, other):

        if not isinstance(other, Q):
            raise TypeError(f"Cannot add instances of {type(self)} and {type(other)}")
        
        obj = Q()
        obj.AND = self.AND + other.AND
        return obj

    def __or__(self, other):

        if not isinstance(other, Q):
            raise TypeError(f"Cannot add instances of {type(self)} and {type(other)}")
        
        obj = Q()
        obj.OR = self.OR + other.OR
        return obj
