"""This module handles functions to convert some types into others"""


from jsonutils.exceptions import JSONConvertException
from jsonutils.functions.dummy import _empty


def dict_to_list(d: dict) -> list:
    """
    Converts from a dict with natural keys to a list, if possible
    """

    def is_int_and_positive(x):
        if isinstance(x, int) and x >= 0:
            return True
        else:
            return False

    if not isinstance(d, dict):
        raise JSONConvertException(
            f"Argument 'd' must be a dict instance, not {type(d)}"
        )

    # first, check that all keys are right
    if not all((is_int_and_positive(k) for k in d)):
        raise JSONConvertException("All dict's keys must be positive integers")

    # initialize output list
    min_index = min(d)
    max_index = max(d)

    if min_index != 0:
        raise JSONConvertException("List have no 0th element defined")

    output_list = [_empty for _ in range(max_index + 1)]
    for k, v in d.items():
        output_list[k] = v

    if _empty in output_list:
        raise JSONConvertException("List items are not connected")
    return output_list
