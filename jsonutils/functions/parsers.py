# This module contains utilities to parse query arguments
# TODO parse image links as text
import ast
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
            if obj.contains_action(target_value):
                pass
            else:
                return False, None
        elif target_action == "in":
            if obj.in_action(target_value):
                pass
            else:
                return False, None
        elif target_action == "regex":
            if obj.regex_action(target_value):
                pass
            else:
                return False, None
        elif target_action == "fullregex":
            if obj.fullregex_action(target_value):
                pass
            else:
                return False, None
        else:
            raise JSONQueryException(f"Bad query: {target_action}")

    return (True, child.parent if include_parent_ else child)


def parse_float(s, decimal_sep=DECIMAL_SEPARATOR, thousands_sep=THOUSANDS_SEPARATOR):
    if decimal_sep == thousands_sep:
        raise JSONSingletonException("Decimal and Thousands separators cannot be equal")
    elif any(x in ("+", "-") for x in (decimal_sep, thousands_sep)):
        raise JSONSingletonException(
            f"Invalid separators:\n\t{decimal_sep}\n\t{thousands_sep}"
        )
    try:
        return float(s)
    except (TypeError, ValueError):
        pass

    pipe = ""  # pipe chain. We'll only add whitespace, punctuations signs and numbers
    has_sign_catched = False
    is_pre_number_character = True  # this will set to False once a number has catched, and won't become True again anymore
    is_post_number_character = False
    is_inside_number = (
        False  # this will be True only if last catched character is part of a number
    )

    for char in s:
        if char.isdigit():
            pipe += char
            is_pre_number_character = False
            is_inside_number = True
        elif is_inside_number and char not in (decimal_sep, thousands_sep):
            is_inside_number = False
            is_post_number_character = True
        elif is_inside_number and is_post_number_character:
            raise JSONSingletonException(f"Can't parse float. Invalid token: {char}")
        elif char in ("-", "+") and not has_sign_catched:
            pipe += char
            has_sign_catched = True
        elif char in ("-", "+") and has_sign_catched:
            raise JSONSingletonException(
                f"Can't parse float. Duplicated sign {char}: {s}"
            )
        elif is_inside_number and char == decimal_sep:
            pipe += "."
        elif char not in ("$", "€", " ") and is_pre_number_character:
            raise JSONSingletonException(
                f"Can't parse float. Alphanumeric characters detected before number: {char}"
            )
    try:
        return float(pipe)
    except Exception as e:
        raise JSONSingletonException(f"Can't parse float. {e}") from None


def parse_datetime(s, only_check=False, tzone_aware=True):
    """
    If only_check is True, then this algorithm will just check if string s matchs a datetime format (no errors).
    Algorithm is tzone aware by default. If no tzone is found on string, UTC will be considered.
    """

    def fill(x):
        if x is None:
            return 0
        else:
            try:
                return int(x)
            except ValueError:
                return

    patterns = (
        r"\s*(?P<year>\d{4})[/\-.](?P<month>\d{1,2})[/\-.](?P<day>\d{1,2})\s*(?:T?\s*(?P<hour>\d{2})[:.](?P<min>\d{2})[:.](?P<sec>\d{2})(?:\.\d{3,}[Zz]?|(?:\.\d{3,})?(?P<off_sign>[+-])(?P<off_hh>\d{2}):(?P<off_mm>\d{2}))?\s*)?",
        r"\s*(?P<day>\d{1,2})[/\-.](?P<month>\d{1,2})[/\-.](?P<year>\d{4})\s*(?:T?\s*(?P<hour>\d{2})[:.](?P<min>\d{2})[:.](?P<sec>\d{2})(?:\.\d{3,}[Zz]?|(?:\.\d{3,})?(?P<off_sign>[+-])(?P<off_hh>\d{2}):(?P<off_mm>\d{2}))?\s*)?",
    )

    for pattern in patterns:
        if match := re.fullmatch(pattern, s):
            if only_check:
                return True

            groups = match.groupdict()
            group_numbers = {k: fill(v) for k, v in groups.items()}

            year = group_numbers.get("year")
            month = group_numbers.get("month")
            day = group_numbers.get("day")
            hour = group_numbers.get("hour")
            min = group_numbers.get("min")
            sec = group_numbers.get("sec")

            off_sign = groups.get("off_sign") or "+"
            off_hh = groups.get("off_hh") or "00"
            off_mm = groups.get("off_mm") or "00"

            tzone = datetime.strptime(f"{off_sign}{off_hh}:{off_mm}", "%z").tzinfo

            try:
                return (
                    datetime(year, month, day, hour, min, sec, tzinfo=tzone)
                    if tzone_aware
                    else datetime(year, month, day, hour, min, sec)
                )
            except Exception as e:
                raise JSONSingletonException(
                    f"Error on introduced datetime. {e}"
                ) from None

    if only_check:
        return False
    raise JSONSingletonException(f"Can't parse target datetime: {s}")


def parse_bool(s):

    if isinstance(s, bool):
        return s

    pipe = s.strip().lower().capitalize()
    if pipe in ("True", "False"):
        return ast.literal_eval(pipe)
    else:
        raise JSONSingletonException(f"Can't parse target bool: {s}")


def parse_json(s):
    # TODO parse jsons in a string
    pass
