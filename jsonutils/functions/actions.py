"""
We define here the interactions between a query and a particular node.
Nodes can be of the following types:
    JSONList, JSONDict, JSONStr, JSONBool, JSONInt, JSONFloat, JSONNull

So we have a total of 56 checks for each action:

JSONList -----> list/tuple
         -----> dict
         -----> str
         -----> datetime
         -----> bool
         -----> int
         -----> float
         -----> null

JSONDict -----> list/tuple
         -----> dict
         -----> str
         -----> datetime
         -----> bool
         -----> int
         -----> float
         -----> null
...
"""

from datetime import datetime
import re
from jsonutils.functions.parsers import parse_datetime, parse_float

from jsonutils.base import JSONBool, JSONDict, JSONFloat, JSONInt, JSONList, JSONNull, JSONStr


def _exact(node, requested_value):
    """
    An exact match.
    In an exact match, only same types are checked, except for JSONStr, which is more versatile.
    """

    if isinstance(node, JSONList):
        if isinstance(requested_value, (list, tuple)):
            return node == list(requested_value)
        else:
            return False
    elif isinstance(node, JSONDict):
        if isinstance(requested_value, dict):
            return node == requested_value
        else:
            return False
    elif isinstance(node, JSONStr):
        if isinstance(requested_value, str):
            # if we are comparing datetimes
            if parse_datetime(
                requested_value, only_check=True
            ):  # if target value is a datetime string
                try:
                    return node.to_datetime() == parse_datetime(requested_value)
                except Exception:
                    return False
            else:  # only comparing strings
                return node == requested_value
        elif isinstance(requested_value, datetime):
            try:
                return node.to_datetime() == requested_value
            except Exception:
                return False
        elif isinstance(requested_value, bool):
            try:
                return node.to_bool() == requested_value
            except Exception:
                return False
        elif isinstance(requested_value, (int, float)):
            try:
                return node.to_float() == requested_value
            except Exception:
                return False
        elif isinstance(requested_value, type(None)):
            if re.fullmatch(r"(?:\s*|null|none|na|nan)?", node, re.I):
                return True
            else:
                return False
        else:
            return False
    elif isinstance(node, JSONBool):
        if isinstance(requested_value, str):
            try:
                return node == requested_value.to_bool()
            except Exception:
                return False
        elif isinstance(requested_value, bool):
            return node == requested_value
        else:
            return False
    elif isinstance(node, (JSONInt, JSONFloat)):
        if isinstance(requested_value, (int, float)):
            return node == requested_value
        elif isinstance(requested_value, str):
            try:
                return node == parse_float(requested_value)
            except Exception:
                return False
        else:
            return False
    elif isinstance(node, JSONNull):
        if isinstance(requested_value, type(None)):
            return node == requested_value
        else:
            return False

def _contains(node, requested_value):
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
    # TODO if self is a number and other too
    if isinstance(node, JSONStr):
        # if target object is an string, contains will return True if target value/s are present within it.
        if isinstance(requested_value, str):
            return requested_value in node
        elif isinstance(requested_value, (float, int)):
            # if target value is a number, we convert it first to a string and then check if it is present within self
            return str(requested_value) in node
        elif isinstance(requested_value, (list, tuple)):
            # if target value is a list, then check if all its items are present in self string
            return all(str(x) in node for x in requested_value)
    elif isinstance(node, JSONDict):
        # if target object is a dict, contains will return True if target value/s are present within its keys.
        if isinstance(requested_value, str):
            return requested_value in node.keys()
        elif isinstance(requested_value, (list, tuple)):
            return all(x in node.keys() for x in requested_value)
    elif isinstance(node, JSONList):
        # if target object is a list, contains will return True if target value are present within its elements.
        if isinstance(requested_value, (list, tuple)):
            return all(x in node for x in requested_value)
        else:
            return True if requested_value in node else False
    elif isinstance(node, JSONBool):
        if isinstance(requested_value, bool):
            return node._data == requested_value
    elif isinstance(node, JSONNull):
        if isinstance(requested_value, type(None)):
            return node._data == requested_value
    return False
