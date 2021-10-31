# Functions to find elements in a JSONObject


from functools import reduce
from operator import getitem
from typing import Dict, List, Tuple, Union

from jsonutils.base import JSONNull, JSONSingleton
from jsonutils.exceptions import JSONConvertException, JSONPathException
from jsonutils.functions.converters import dict_to_list
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


def is_iterable(obj):
    """Check if obj is an iterable"""
    try:
        _ = iter(obj)
    except TypeError:
        return False

    return True


def _eval_object(obj, iterable):
    """Eval composed object on iterable path"""

    if not is_iterable(iterable):
        raise TypeError(
            f"Argument 'iterable' must be an iterable, not {type(iterable)}"
        )

    return reduce(getitem, iterable, obj)


def _set_object(obj, iterable, value):
    """
    The generalization of setitem for nested paths.
    First, it retrieves the iterable[:-1] item, and then it calls setitem method over such an item.
    """
    if not isinstance(iterable, (list, tuple)):
        raise TypeError(
            f"Argument 'iterable' must be a tuple or list instance, not {type(iterable)}"
        )
    get_path = iterable[:-1]
    set_path = iterable[-1]
    retrieved_obj = _eval_object(obj, get_path)
    retrieved_obj[set_path] = value


def _check_types(path, value):
    """
    Assert path and value has the right types
    """
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
    if not isinstance(iterable, list):
        raise TypeError(f"Argument 'iterable' must be a list, not {type(iterable)}")

    if not iterable:
        raise ValueError(
            "Argument 'iterable' must have a length greater or equals than 1"
        )
    initial_dict = DefaultDict()

    for path, value in iterable:
        # check path and value have right types (path is a list or tuple, and value is not composed)
        _check_types(path, value)
        # build the schema dict inline
        try:
            _set_object(initial_dict, path, value)
        except Exception as e:
            raise JSONPathException(f"node structure is incompatible. {e}")

    # change inner dict by lists
    # we must serialize the default dict
    serialized_dict = initial_dict.serialize()
    output = _find_listable_dicts(serialized_dict)

    return output


class DefaultList(list):

    __osetitem__ = list.__setitem__
    __ogetitem__ = list.__getitem__

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj.parent = None
        obj.key = None
        obj.index = 0
        return obj

    def __getitem__(self, i):
        try:
            return super().__getitem__(i)
        except IndexError:
            pass
        except TypeError:
            pass


class DefaultDict(dict):
    """A dict schema with no nested lists"""

    __osetitem__ = dict.__setitem__
    __ogetitem__ = dict.__getitem__

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        obj.parent = None
        obj.key = None
        return obj

    @staticmethod
    def _dictsuperset(obj, k, v=None):
        """
        Like a regular dict's setitem method, but with assigning parents to value if needed
        """

        if v is None:
            v = DefaultDict()
        if isinstance(v, DefaultDict):
            v.parent = obj
            v.key = k
        obj.__osetitem__(k, v)
        return obj.__ogetitem__(k)

    @staticmethod
    def _listsuperset(obj, key, idx):
        if obj is None:
            return

        def_list = DefaultList()
        def_list.parent = obj
        def_list.key = key
        def_list.index = idx
        obj.__osetitem__(key, def_list)
        return obj.__ogetitem__(key)  # returns a DefaultList

    def __getitem__(self, k):

        try:  # if k is already a key in dict, return its value
            return super().__getitem__(k)
        except KeyError:  # if key is not in dict, set it with an empty DefaultDict or DefaultList
            if isinstance(k, str):
                self._dictsuperset(self, k)  # set item and assign parent attributes
                return super().__getitem__(k)
            elif isinstance(k, int):
                parent = self.parent
                key = self.key
                self._listsuperset(parent, key, k)
                return parent.__ogetitem__(key)

    def __setitem__(self, k, v):
        try:
            super().__getitem__(k)
        except KeyError:  # only set item if it is not already registered
            return self._dictsuperset(self, k, v)
        raise Exception(f"Key {k} is already registered")

    @staticmethod
    def _serialize(obj, new_obj=None):
        if new_obj is None:
            new_obj = {}
        for k, v in obj.items():
            if isinstance(v, DefaultDict):
                v = dict(v)
            new_obj[k] = v
            if isinstance(v, dict):
                DefaultDict._serialize(v, new_obj[k])
        return new_obj

    def serialize(self):
        """Returns a new Python's native dict from a DefaultDict object"""

        return self._serialize(self)


def _find_listable_dicts(d: dict, new_obj: dict = None):
    """Traverse recursively over nested dict, and change listable dicts by their corresponding lists"""
    if new_obj is None:
        new_obj = {}
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict):
                try:
                    v = dict_to_list(v)
                except JSONConvertException:
                    pass
            new_obj[k] = v
            _find_listable_dicts(v, new_obj[k])
    elif isinstance(d, list):
        for i, v in enumerate(d):
            if isinstance(v, dict):
                try:
                    v = dict_to_list(v)
                except JSONConvertException:
                    pass
            new_obj[i] = v
            _find_listable_dicts(v, new_obj[i])

    return new_obj


if __name__ == "__main__":
    x = DefaultDict()
    x["A"][0]["A"] = 1
