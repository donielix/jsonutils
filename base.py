# This module contains the base objects needed
import json
from datetime import datetime

from config.locals import DECIMAL_SEPARATOR, THOUSANDS_SEPARATOR
from config.queries import INCLUDE_PARENTS, RECURSIVE_QUERIES
from encoders import JSONObjectEncoder
from queryutils import QuerySet, _parse_datetime, _parse_float, parse_query


class JSONObject:
    """
    This class acts as a switcher. It will return the corresponding object instance for a given data.
    This class does not contain any instances of.
    """

    def __new__(cls, data):

        if isinstance(data, dict):
            return JSONDict(data)
        elif isinstance(data, list):
            return JSONList(data)
        elif isinstance(data, bool):
            return JSONBool(data)
        elif isinstance(data, type(None)):
            return JSONNone(data)
        elif isinstance(data, str):
            return JSONStr(data)
        elif isinstance(data, float):
            return JSONFloat(data)
        elif isinstance(data, int):
            return JSONInt(data)
        else:
            raise TypeError(f"Wrong data's format: {type(data)}")


class JSONMaster:
    """
    This is the base class for all JSON objects (compose or singleton).

    Attributes:
    -----------
        _child_objects:
        key: last dict parent key where the object comes from
        index: las list parent index where the object comes from
        parent: last parent object where this object comes from
    """

    def __init__(self, *args, **kwargs):

        self._child_objects = []
        self.key = None
        self.index = None
        self.parent = None

    def json_encode(self, **kwargs):
        return json.dumps(self, cls=JSONObjectEncoder, **kwargs)

    @property
    def json_data(self):
        return json.loads(json.dumps(self, cls=JSONObjectEncoder))


class JSONCompose(JSONMaster):
    """
    This is the base class for JSON composed objects.
    Composed objects can be dict or list instances.
    Composed objects can send queries to children (which can be also compose or singleton objects)
    """

    is_composed = True

    def __init__(self, *args, **kwargs):
        """
        By initializing instance, it assign types to child items
        """
        super().__init__(*args, **kwargs)
        self._assign_childs()

    def _assign_childs(self):
        """Any JSON object can be a child for a given compose object"""

        if isinstance(self, JSONDict):
            for key, value in self.items():
                child = JSONObject(value)
                child.key = key
                child.parent = self
                self.__setitem__(key, child)
                self._child_objects.append(child)

        elif isinstance(self, JSONList):
            for index, item in enumerate(self):
                child = JSONObject(item)
                child.index = index
                child.parent = self
                self.__setitem__(index, child)
                self._child_objects.append(child)

    def query(self, recursive_=RECURSIVE_QUERIES, include_parent_=INCLUDE_PARENTS, **q):
        queryset = QuerySet()
        childs = self._child_objects
        for child in childs:
            # if child satisfies query request, it will be appended to the queryset object
            if parse_query(child, **q):
                if include_parent_:
                    queryset.append(child.parent)
                else:
                    queryset.append(child)
            # if child is also a compose object, it will send the same query to its children recursively
            if child.is_composed and recursive_:
                queryset += child.query(include_parent_=include_parent_, **q)
        return queryset


class JSONSingleton(JSONMaster):
    """
    This is the base class for JSON singleton objects
    """

    is_composed = False

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


# ---- COMPOSE OBJECTS ----
class JSONDict(dict, JSONCompose):
    """ """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        JSONCompose.__init__(self, *args, **kwargs)


class JSONList(list, JSONCompose):
    """ """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        JSONCompose.__init__(self, *args, **kwargs)


# ---- SINGLETON OBJECTS ----
class JSONStr(str, JSONSingleton):
    # converters
    def to_float(
        self, decimal_sep=DECIMAL_SEPARATOR, thousands_sep=THOUSANDS_SEPARATOR
    ):
        """
        Try to parse a python float64 from self string.
        Examples:
        --------
        >> from base import JSONStr
        >> JSONStr(" $5.3USD ").to_float()
            5.3
        >> JSONStr(" -$ 4,450,326.58 ").to_float()
            -4450326.58
        """

        return _parse_float(self, decimal_sep, thousands_sep)

    def to_datetime(self):
        """Try to parse a naive datetime object from self string"""

        return _parse_datetime(self)

    # comparison magic methods
    # if data types are not compatible, then return False
    # when querying, other will correspond to target query value (ex: Float__gt=<other>)
    def __eq__(self, other):
        # if target_value is a number
        if isinstance(other, (float, int)):
            try:
                return self.to_float() == other
            except Exception:
                return False
        # if target_value is a datetime
        elif isinstance(other, datetime):
            try:
                return self.to_datetime() == other
            except Exception:
                return False
        else:
            return super().__eq__(other)

    def __gt__(self, other):
        # if target_value is a number
        if isinstance(other, (float, int)):
            try:
                return self.to_float() > other
            except Exception:
                return False
        # if target_value is a datetime
        elif isinstance(other, datetime):
            try:
                return self.to_datetime() > other
            except Exception:
                return False
        else:
            return super().__gt__(other)

    def __ge__(self, other):
        # if target_value is a number
        if isinstance(other, (float, int)):
            try:
                return self.to_float() >= other
            except Exception:
                return False
        # if target_value is a datetime
        elif isinstance(other, datetime):
            try:
                return self.to_datetime() >= other
            except Exception:
                return False
        else:
            return super().__ge__(other)

    def __lt__(self, other):
        if isinstance(other, (float, int)):
            try:
                return self.to_float() < other
            except Exception:
                return False


class JSONFloat(float, JSONSingleton):
    pass


class JSONInt(int, JSONSingleton):
    pass


class JSONBool(JSONSingleton):
    def __init__(self, data):

        if not isinstance(data, bool):
            raise TypeError(f"Argument is not a valid boolean type: {type(data)}")
        super().__init__()
        self._data = data

    def __repr__(self):
        return str(self._data)

    def __bool__(self):
        return self._data

    def __eq__(self, other):
        return self._data == other


class JSONNone(JSONSingleton):
    def __init__(self, data):

        if not isinstance(data, type(None)):
            raise TypeError(f"Argument is not a valid None type: {type(data)}")
        super().__init__()
        self._data = data

    def __repr__(self):
        return "None"

    def __bool__(self):
        return False

    def __eq__(self, other):
        return self._data == other
