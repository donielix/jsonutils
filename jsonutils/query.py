from datetime import datetime

from jsonutils.exceptions import JSONQueryException


class SingleQuery:
    """
    This class represents a single query object.
    It consists of a single key and a collection of actions that operate on that key.

    Arguments:
    ---------
        k: key part of the query
        v: target value of the query
    """

    def __init__(self, query_key, query_value):

        if not isinstance(
            query_value,
            (float, int, str, type(None), bool, dict, list, tuple, datetime),
        ):
            raise JSONQueryException(
                f"Target value of query has invalid type: {type(query_value)}. Valid types are: float, int, str, None, bool, dict, list, tuple, datetime"
            )

        self.target_value = query_value
        self._parse_key(query_key)

    def _parse_key(self, query_key):
        # TODO

        splitted = [i for i in query_key.split("__") if i]

        if not splitted:
            raise JSONQueryException("Bad query. Missing target key")

        self.target_key = splitted[0]
        self.target_actions = splitted[1:]

    def _check_against_child(self, child):
        """Check this single query against a target child object"""
        from jsonutils.base import JSONNode

        # TODO
        if not isinstance(child, JSONNode):
            raise JSONQueryException(
                f"child argument must be JSONNode type, not {type(child)}"
            )
        pass


class Q:
    """
    A Query object. We can join different queries by means of bitand and bitor operators (& |)
    Examples
    --------
    >> obj = JSONObject(
        [
            {
                "timestamp": "2021-05-01 09:00:00",
                "value": [0.5, 0.87]
            },
            {
                "timestamp": "2021-04-02 10:30:00",
                "value": [-0.23, 1]
            },
            {
                "timestamp": "2021-06-01 08:25:30",
                "value": [0.9, 0.15]
            }
        ]
    )

    >> obj.query(Q(timestamp__gt="2021-05-01 10:00:00") | Q(value__0__gte=0.5))
        [{"timestamp": "2021-05-01 09:00:00","value": [0.5, 0.87]},{"timestamp": 2021-06-01 08:25:30, "value": [0.9, 0.15]}]
    """

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


class QuerySet(list):
    """
    This is a queryset object.
    Attributes:
    ----------
        _root: the root json object from which the entire queryset is derived
    """

    def __init__(self, *args):
        super().__init__(*args)
        self._root = None

    def first(self):
        return self.__getitem__(0) if self.__len__() > 0 else None

    def last(self):
        return self.__getitem__(-1) if self.__len__() > 0 else None

    def exists(self):
        return True if self.__len__() > 0 else False

    def update(self, new_obj):
        """
        Update elements of queryset within JSONObject from which they are derived (self._root)
        """
        from jsonutils.base import JSONObject

        # TODO allow for functions over the objects
        for item in self:
            path = item.jsonpath.relative_to(self._root)
            exec(f"self._root{path} = new_obj")

        return self._root
