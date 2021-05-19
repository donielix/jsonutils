# This module contains the base objects needed
import ast
import json
import re
from datetime import datetime

from jsonutils.config.locals import DECIMAL_SEPARATOR, THOUSANDS_SEPARATOR
from jsonutils.config.queries import CLEVER_PARSING, INCLUDE_PARENTS, RECURSIVE_QUERIES
from jsonutils.encoders import JSONObjectEncoder
from jsonutils.parsers import QuerySet, _parse_query, parse_datetime, parse_float


class JSONPath:
    """
    Object representing a JSON path for a given JSON object.
    Don't instanciate it directly.
    """

    def __new__(cls, s=""):
        obj = super().__new__(cls)
        obj._string = s  # pretty path
        obj._path = ""  # python json path
        return obj

    @property
    def data(self):
        return self._string

    @property
    def expr(self):
        return self._path

    def _update(self, **kwargs):
        if (key := kwargs.get("key")) is not None:
            self._string = str(key) + "/" + self._string
            self._path = f'["{key}"]' + self._path
        elif (index := kwargs.get("index")) is not None:
            self._string = str(index) + "/" + self._string
            self._path = f"[{index}]" + self._path

    def __eq__(self, other):
        return (self._string == other) or (self._path == other)

    def __repr__(self):
        return self._string


class JSONObject:
    """
    This class acts as a switcher. It will return the corresponding object instance for a given data.
    This class does not contain any instances of.
    """

    def __new__(cls, data):

        if isinstance(data, dict):
            return JSONDict(data)
        elif isinstance(data, (list, tuple)):
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

    @property
    def jsonpath(self):
        parent = self
        path = JSONPath()
        while parent is not None:
            path._update(key=parent.key, index=parent.index)
            parent = parent.parent
        return path

    @property
    def root(self):
        """Get root object"""
        parent = self
        last = parent
        while parent is not None:
            last = parent
            parent = parent.parent
        return last

    # ---- ACTION METHODS ----
    def contains(self, other):
        """
        This method analyzes whether a given JSONObject contains the object specified by the <other> parameter, and returns a boolean.
        <self> will be the current child instance within the JSONObject, whereas <other> will be the current query target value.
        Examples in a query method:
        --------------------------
        >> obj = JSONObject(
            {
                "data": {
                    "cik": "0008547852",
                    "country": "USA",
                    "live": False
                },
                "team": [
                    "Daniel",
                    "Alex",
                    "Catherine",
                    None
                ]
            }
        )

        >> obj.query(data__contains="cik")  # in this case the "cik" string object will play the role of <other> (the target query value).
                                            # On the other hand, <self> in this case will take the value of the "data" dictionary (JSONDict)
            [{'cik': '0008547852', 'country': 'USA', 'live': False}]

        >> obj.query(cik__contains=85) # now the 85 integer object will be <other> object, whereas <self> will be the "cik" string object.
            ['0008547852']

        >> obj.query(team__contains=["Alex", "Daniel"]) # in this case target JSONObject must contains both "Alex" and "Daniel" strings
            [['Daniel', 'Alex', 'Catherine', None]]

        >> obj.query(team__contains=None).first()
            ['Daniel', 'Alex', 'Catherine', None]
        """
        # TODO implement clever parsing
        if isinstance(self, JSONStr):
            # if target object is an string, contains will return True if target value/s are present within it.
            if isinstance(other, str):
                return other in self
            elif isinstance(other, (float, int)):
                # if target value is a number, we convert it first to a string and then check if it is present within self
                return str(other) in self
            elif isinstance(other, (list, tuple)):
                # if target value is a list, then check if all its items are present in self string
                return all(str(x) in self for x in other)
        elif isinstance(self, JSONDict):
            # if target object is a dict, contains will return True if target value/s are present within its keys.
            if isinstance(other, str):
                return other in self.keys()
            elif isinstance(other, (list, tuple)):
                return all(x in self.keys() for x in other)
        elif isinstance(self, JSONList):
            # if target object is a list, contains will return True if target value are present within its elements.
            if isinstance(other, (list, tuple)):
                return all(x in self for x in other)
            else:
                return True if other in self else False
        elif isinstance(self, JSONBool):
            if isinstance(other, bool):
                return self._data == other
        return False

    def isin(self, other):
        """
        This method, as opposed to "contains", analyzes whether a given JSONObject is contained in the iterable object specified
        by the <other> parameter
        """
        # TODO complete isin child method
        if isinstance(self, (JSONSingleton)):
            if isinstance(other, (str, list, tuple, dict)):
                return self in other
        elif isinstance(self, JSONList):
            if isinstance(other, (list, tuple)):
                return all(x in other for x in self)
        elif isinstance(self, JSONDict):
            if isinstance(other, (list, tuple)):
                return all(x in other for x in self.keys())
        return False

    def regex(self, other):
        """
        This method analyzes whether a given JSONObject matchs with target regex pattern specified by <other>.
        """
        if isinstance(self, JSONStr):
            if isinstance(other, (str, re.Pattern)):
                return bool(re.search(other, self))
        elif isinstance(self, (JSONInt, JSONFloat)):
            if isinstance(other, (str, re.Pattern)):
                return bool(re.search(other, str(self)))
        return False

    def fullregex(self, other):
        """
        This method analyzes whether a given JSONObject full matchs with target regex pattern specified by <other>.
        """
        if isinstance(self, JSONStr):
            if isinstance(other, (str, re.Pattern)):
                return bool(re.fullmatch(other, self))
        elif isinstance(self, (JSONInt, JSONFloat)):
            if isinstance(other, (str, re.Pattern)):
                return bool(re.fullmatch(other, str(self)))
        return False


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
            check, obj = _parse_query(child, include_parent_, **q)
            if check:
                queryset.append(obj)
            # if child is also a compose object, it will send the same query to its children recursively
            if child.is_composed and recursive_:
                queryset += child.query(include_parent_=include_parent_, **q)
        return queryset


class JSONSingleton(JSONMaster):
    """
    This is the base class for JSON singleton objects.
    A singleton object has no children
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

        return parse_float(self, decimal_sep, thousands_sep)

    def to_datetime(self):
        """Try to parse a naive datetime object from self string"""

        return parse_datetime(self)

    # comparison magic methods
    # if data types are not compatible, then return False (no error thrown)
    # when querying, other will correspond to target query value (ex: Float__gt=<other>)
    # TODO implement clever parsing option
    def __eq__(self, other):
        # if target_value is a number, we first convert self str instance to float
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
        # if target_value is a str
        elif isinstance(other, str):
            if parse_datetime(
                other, only_check=True
            ):  # if target value is a datetime string
                try:
                    return self.to_datetime() == parse_datetime(other)
                except Exception:
                    return False
            else:
                try:
                    return super().__eq__(other)
                except Exception:
                    return False
        # otherwise (maybe list, dict, none, bool) call parent __eq__ (from str)
        else:
            try:
                return super().__eq__(other)
            except Exception:
                return False

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
        # if target_value is a str
        elif isinstance(other, str):
            if parse_datetime(
                other, only_check=True
            ):  # if target value is a datetime string
                try:
                    return self.to_datetime() > parse_datetime(other)
                except Exception:
                    return False
            else:
                try:
                    return super().__gt__(other)
                except Exception:
                    return False
        # otherwise (maybe list, dict, none, bool)
        else:
            try:
                return super().__gt__(other)
            except Exception:
                return False

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
        # if target_value is a str
        elif isinstance(other, str):
            if parse_datetime(
                other, only_check=True
            ):  # if target value is a datetime string
                try:
                    return self.to_datetime() >= parse_datetime(other)
                except Exception:
                    return False
            else:
                try:
                    return super().__ge__(other)
                except Exception:
                    return False
        # otherwise (maybe list, dict, none, bool)
        else:
            try:
                return super().__ge__(other)
            except Exception:
                return False

    def __lt__(self, other):
        # if target_value is a number
        if isinstance(other, (float, int)):
            try:
                return self.to_float() < other
            except Exception:
                return False
        # if target_value is a datetime
        elif isinstance(other, datetime):
            try:
                return self.to_datetime() < other
            except Exception:
                return False
        # if target_value is a str
        elif isinstance(other, str):
            if parse_datetime(
                other, only_check=True
            ):  # if target value is a datetime string
                try:
                    return self.to_datetime() < parse_datetime(other)
                except Exception:
                    return False
            else:
                try:
                    return super().__lt__(other)
                except Exception:
                    return False
        # otherwise (maybe list, dict, none, bool)
        else:
            try:
                return super().__lt__(other)
            except Exception:
                return False

    def __le__(self, other):
        # if target_value is a number
        if isinstance(other, (float, int)):
            try:
                return self.to_float() <= other
            except Exception:
                return False
        # if target_value is a datetime
        elif isinstance(other, datetime):
            try:
                return self.to_datetime() <= other
            except Exception:
                return False
        # if target_value is a str
        elif isinstance(other, str):
            if parse_datetime(
                other, only_check=True
            ):  # if target value is a datetime string
                try:
                    return self.to_datetime() <= parse_datetime(other)
                except Exception:
                    return False
            else:
                try:
                    return super().__le__(other)
                except Exception:
                    return False
        # otherwise (maybe list, dict, none, bool)
        else:
            try:
                return super().__le__(other)
            except Exception:
                return False


class JSONFloat(float, JSONSingleton):
    # TODO implement comparison methods
    def __eq__(self, other):
        if isinstance(other, str):
            try:
                return super().__eq__(parse_float(other))
            except Exception:
                return False
        else:
            try:
                return super().__eq__(other)
            except Exception:
                return False


class JSONInt(int, JSONSingleton):
    # TODO implement comparison methods
    def __eq__(self, other):
        if isinstance(other, str):
            try:
                return super().__float__().__eq__(parse_float(other))
            except Exception:
                return False
        else:
            try:
                return super().__eq__(other)
            except Exception:
                return False


class JSONBool(JSONSingleton):
    # TODO implement comparison methods
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
        if isinstance(other, JSONBool):
            return self._data == other._data
        elif isinstance(other, str):
            try:
                expr = ast.literal_eval(other.capitalize())
                if not isinstance(expr, bool):
                    return False
                return self._data == expr
            except Exception:
                return False
        elif not isinstance(other, bool):
            return False
        else:
            try:
                return self._data == other
            except Exception:
                return False

    def __gt__(self, other):
        return False


class JSONNone(JSONSingleton):
    # TODO implement comparison methods
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
