# Functions to find elements in a JSONObject


from functools import reduce
from operator import getitem
from typing import Dict, List, Tuple, Union

from jsonutils.base import JSONNull, JSONSingleton
from jsonutils.exceptions import JSONPathException
from jsonutils.functions.dummy import _empty, _EmptyType


def _inner_join_overwriting_with_null(node1, node2):
    """
    In an inner_join, an output will only be returned if both nodes are non _empty.
    When overwrite_with_null=True, then we return always node2, regardless of whether it is null or not.
    """
    if any(isinstance(node, _EmptyType) for node in (node1, node2)):
        return _empty
    return node2


def _inner_join_non_overwriting_with_null(node1, node2):
    """
    In an inner_join, an output will only be returned if both nodes are non _empty.
    When overwrite_with_null=False, then we return node2 only if it is not null.
    Otherwise, node1 will be returned.
    """
    if any(isinstance(node, _EmptyType) for node in (node1, node2)):
        return _empty
    return node2 if not isinstance(node2, JSONNull) else node1


def _outer_join_overwriting_with_null(node1, node2):
    """
    In an outer_join, the non-empty value will be returned. If both nodes are empty then
    the output will be an _empty class.
    When overwrite_with_null=True, then we return always node2, regardless of whether it is null or not.
    """
    empty_number = 0
    args = (node1, node2)
    for idx, node in enumerate(args):
        if isinstance(node, _EmptyType):
            empty_number += 1
            empty_id = idx
    if empty_number == 2:
        return _empty
    if empty_number == 1:
        return args[empty_id - 1]
    return node2


def _outer_join_non_overwriting_with_null(node1, node2):
    """
    In an outer_join, the non-empty value will be returned. If both nodes are empty then
    the output will be an _empty class.
    When overwrite_with_null=False, then we return node2 only if it is not null.
    Otherwise, node1 will be returned.
    """

    empty_number = 0
    args = (node1, node2)
    for idx, node in enumerate(args):
        if isinstance(node, _EmptyType):
            empty_number += 1
            empty_id = idx
    if empty_number == 2:
        return _empty
    if empty_number == 1:
        return args[empty_id - 1]
    return node2 if not isinstance(node2, JSONNull) else node1


def _left_join_overwriting_with_null(node1, node2, direct_order=True):
    """
    In a left_join, we keep the left node when any of the two nodes are _empty.
    """

    if isinstance(node1, _EmptyType):
        return _empty
    if isinstance(node2, _EmptyType):
        return node1

    return (
        _inner_join_overwriting_with_null(node1, node2)
        if direct_order
        else _inner_join_overwriting_with_null(node2, node1)
    )


def _left_join_non_overwriting_with_null(node1, node2, direct_order=True):
    """
    In a left_join, we keep the left node when any of the two nodes are _empty.
    """

    if isinstance(node1, _EmptyType):
        return _empty
    if isinstance(node2, _EmptyType):
        return node1

    return (
        _inner_join_non_overwriting_with_null(node1, node2)
        if direct_order
        else _inner_join_non_overwriting_with_null(node2, node1)
    )


def _right_join_overwriting_with_null(node1, node2):
    """
    In a right_join, we keep the right node when any of the two nodes are _empty.
    """

    return _left_join_overwriting_with_null(node2, node1, direct_order=False)


def _right_join_non_overwriting_with_null(node1, node2):
    """
    In a right_join, we keep the right node when any of the two nodes are _empty.
    """

    return _left_join_non_overwriting_with_null(node2, node1, direct_order=False)


def _choose_value(node1, node2, overwrite_with_null=True, merge_type="inner_join"):
    """
    Given two singleton nodes with the same path as arguments, choose an appropiate output node.
    Preference order by default: singleton > null > empty

    Arguments
    ---------
        node1: a node type, or _empty
        node2: a node type, or _empty
        overwrite_with_null: type of behaviour when a null value is found on node2
        merge_type: type of behaviour when a missing path is found (node1 or node2 is _empty)
    Returns
    -------
        A node object or _empty
    """
    # TODO define a compose method which call this private function over all its elements,
    # with an append_compose option (if True, then composed objects (dict and list) will be appended)
    # ---- TYPE CHECK ----

    if not all(isinstance(x, (JSONSingleton, _EmptyType)) for x in (node1, node2)):
        raise TypeError(
            f"First two arguments must be node or empty instances:\n{type(node1)}\n{type(node2)}"
        )

    if not isinstance(merge_type, str):
        raise TypeError(
            f"Argument 'merge_type' must be an str instance, not {type(merge_type)}"
        )

    merge_type = merge_type.lower().strip()

    if not isinstance(overwrite_with_null, bool):
        raise TypeError(
            f"Argument 'overwrite_with_null' must be a bool instance, not {type(overwrite_with_null)}"
        )

    if not merge_type in ("inner_join", "outer_join", "left_join", "right_join"):
        raise ValueError(
            f"Argument 'merge_type' must be one of the following: 'inner_join', 'outer_join', 'left_join', 'right_join'"
        )

    # --- variation cases ----
    # We have 3 elements (NA, empty, singleton) that we have to arrange in pairs, allowing repetitions.
    # So, the number of variations will be 3^2 = 9.
    # Note that the combination "empty, empty" is not possible. However, we include it for consistency
    # =========== combinations ============
    #    node1                     node2
    # =====================================
    #     NA                        NA
    #     NA                       empty
    #    empty                      NA
    #    empty                     empty
    #     NA                      singleton
    #  singleton                    NA
    #    empty                    singleton
    #  singleton                   empty
    #  singleton                  singleton

    if merge_type == "inner_join":
        if overwrite_with_null:
            return _inner_join_overwriting_with_null(node1, node2)
        else:
            return _inner_join_non_overwriting_with_null(node1, node2)
    if merge_type == "outer_join":
        if overwrite_with_null:
            return _outer_join_overwriting_with_null(node1, node2)
        else:
            return _outer_join_non_overwriting_with_null(node1, node2)
    if merge_type == "left_join":
        if overwrite_with_null:
            return _left_join_overwriting_with_null(node1, node2)
        else:
            return _left_join_non_overwriting_with_null(node1, node2)
    if merge_type == "right_join":
        if overwrite_with_null:
            return _right_join_overwriting_with_null(node1, node2)
        else:
            return _right_join_non_overwriting_with_null(node1, node2)


def _eval_object(obj, iterable):
    """Eval composed object on iterable path"""
    return reduce(getitem, iterable, obj)


def _check_types(path, value):
    """Assert path and value has the right types"""
    if not isinstance(path, (tuple, list)):
        raise TypeError(
            f"First element of iterables must be a tuple object with json path items, not {type(path)}"
        )
    if isinstance(value, (str, float, int, bool, type(None))) or value in (
        {},
        [],
    ):
        pass
    else:
        raise TypeError(f"Path's value must be a singleton, not {value}")


def _initialize_objects(path):
    """Given a path, check if it corresponds to a dict or list parent object, and initialize it"""
    try:
        root_key = path[0]
    except IndexError:
        raise JSONPathException(
            f"Paths must be a tuple iterable with at least one item, not {path}"
        )
    if isinstance(root_key, str):
        is_dict = True
        is_list = False
        obj = {}
    elif isinstance(root_key, int):
        is_dict = False
        is_list = True
        obj = []
    else:
        raise ValueError(
            f"Path items must be an 'str' or 'int' instances, not {type(root_key)}"
        )
    return obj, is_dict, is_list


def _json_from_path(iterable: List[Tuple]) -> Union[Dict, List]:
    """
    Build a JSONObject from a list of path/value pairs.
    Examples
    --------

    >> res = JSONObject.from_path(
        [
            (
                ("A", "B"),
                True
            ),
            (
                ("A", "C"),
                False
            )
        ]
    )
    >> res
        {
            "A": {
                "B": True,
                "C": False
            }
        }
    """
    # TODO complete
    if not isinstance(iterable, (list, tuple)):
        raise TypeError(
            f"Argument 'iterable' must be an iterable, not {type(iterable)}"
        )
    length = len(iterable)

    root_key_check = False
    while length:
        for path, value in iterable:
            _check_types(path, value)

            if (
                not root_key_check
            ):  # first time, we check the type and initialize object
                obj, is_dict, is_list = _initialize_objects(path)
                root_key_check = True
