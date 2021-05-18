# This module contains utilities to parse query arguments
# TODO parse image links as text
import re
from datetime import datetime

from jsonutils.config.locals import DECIMAL_SEPARATOR, THOUSANDS_SEPARATOR
from jsonutils.exceptions import JSONQueryException, JSONSingletonException


def _parse_query(child, include_parent_, **q):
    """
    We must determine whether the child passed as input argument matches the conditions given by the query q.
    If required actions don't match the child type, it won't throw any exception, just returns False for such an object, and
    it won't be appended to the queryset.
    Query q must be structured as follows:
        <key>__<modificator>__<query>
    """
    # TODO if a query contains two different keys, take into account the dict
    # TODO __lower action and __child__<child> modificator, to perform before other actions

    obj = child

    for query_key, query_value in q.items():
        if not isinstance(
            query_value,
            (float, int, str, type(None), bool, dict, list, tuple, datetime),
        ):
            raise JSONQueryException(
                f"Target value of query has invalid type: {type(query_value)}. Valid types are: float, int, str, None, bool, dict, list, tuple, datetime"
            )
        splitted = query_key.split("__")
        target_key = splitted[0]
        if not target_key:
            raise JSONQueryException("Bad query. Missing target key")
        # first of all, if target key of query argument does not match child's key, we won't append it to querylist
        if target_key != child.key:
            return False, None
        try:
            target_action = splitted[1]
        except IndexError:  # default action will be exact value match
            target_action = "exact"
        else:
            try:
                target_action_extra = splitted[2]
            except IndexError:
                target_action_extra = None
        target_value = query_value  # this is the query argument value
        # ---- MODIFICATORS ----
        # modify obj before apply actions
        if target_action == "parent":
            obj = child.parent
            target_action = target_action_extra if target_action_extra else "exact"
        elif target_action.isdigit():  # if a digit, take such an element
            try:
                obj = child[int(target_action)]
            except Exception:  # if not a list
                return False, None
            else:
                target_action = target_action_extra if target_action_extra else "exact"
        # ---- MATCH ----
        # all comparisons have child object to the left, and the underlying algorithm is contained in the magic methods of the JSON objects
        # no errors will be thrown, if types are not compatible, just returns False

        if target_action == "exact":
            # child value must match with target value of query
            if obj == target_value:
                pass
            else:
                return False, None
        elif target_action == "gt":
            # child value must be greather than target value of query
            if obj > target_value:
                pass
            else:
                return False, None
        elif target_action == "gte":
            if obj >= target_value:
                pass
            else:
                return False, None
        elif target_action == "lt":
            if obj < target_value:
                pass
            else:
                return False, None
        elif target_action == "lte":
            if obj <= target_value:
                pass
            else:
                return False, None
        elif target_action == "contains":
            if obj.contains(target_value):
                pass
            else:
                return False, None
        elif target_action == "in":
            if obj.isin(target_value):
                pass
            else:
                return False, None
        elif target_action == "regex":
            if obj.regex(target_value):
                pass
            else:
                return False, None
        else:
            raise JSONQueryException(f"Bad query: {target_action}")

    return (True, child.parent if include_parent_ else child)


def parse_float(s, decimal_sep=DECIMAL_SEPARATOR, thousands_sep=THOUSANDS_SEPARATOR):
    if decimal_sep == thousands_sep:
        raise JSONSingletonException("Decimal and Thousands separators cannot be equal")
    pipe = re.sub(r"[^0-9\s,.+-]", "", s)  # keep only [0-9] whitespaces , . + -
    pipe = re.sub(r"(?<=[+-])\s+", "", pipe)  # remove whitespace after +-
    pipe = pipe.replace(thousands_sep, "").replace(decimal_sep, ".")

    return float(pipe)


def parse_datetime(s, only_check=False):
    """If only_check is True, then this algorithm will just check if string s matchs a datetime format (no errors)"""
    # TODO check patterns'end wildcards
    patterns = (
        r"\s*(?P<year>\d{4})[/\-.](?P<month>\d{1,2})[/\-.](?P<day>\d{1,2})\s*",
        r"\s*(?P<day>\d{1,2})[/\-.](?P<month>\d{1,2})[/\-.](?P<year>\d{4})\s*",
        r"\s*(?P<year>\d{4})[/\-.](?P<month>\d{1,2})[/\-.](?P<day>\d{1,2})\s*T?\s*(?P<hour>\d{2})[:.](?P<min>\d{2})[:.](?P<sec>\d{2}).*",
        r"\s*(?P<day>\d{1,2})[/\-.](?P<month>\d{1,2})[/\-.](?P<year>\d{4})\s*T?\s*(?P<hour>\d{2})[:.](?P<min>\d{2})[:.](?P<sec>\d{2}).*",
    )
    for pattern in patterns:
        if match := re.fullmatch(pattern, s):
            if only_check:
                return True
            group_dict = {k: int(v) for k, v in match.groupdict().items()}
            year = group_dict.get("year")
            month = group_dict.get("month")
            day = group_dict.get("day")
            hour = group_dict.get("hour", 0)
            min = group_dict.get("min", 0)
            sec = group_dict.get("sec", 0)
            return datetime(year, month, day, hour, min, sec)
    if only_check:
        return False
    raise JSONSingletonException(f"Can't parse target datetime: {s}")


class QuerySet(list):
    def first(self):
        return self.__getitem__(0) if self.__len__() > 0 else None

    def last(self):
        return self.__getitem__(-1) if self.__len__() > 0 else None

    def exists(self):
        return True if self.__len__() > 0 else False
