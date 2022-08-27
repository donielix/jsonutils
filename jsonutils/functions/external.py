"""
We put here all references to third packages functions or methods
"""
import sys
from typing import Any

from jsonutils.functions.decorators import return_value_on_exception


@return_value_on_exception(False)
def isPandasNAN(instance: Any, fail_silently: bool = True) -> bool:

    isna = sys.modules["pandas"].isna
    result = isna(instance)
    if not isinstance(result, bool):
        return False
    return result


def DjangoQuerySet():

    try:
        return sys.modules["django"].db.models.QuerySet
    except Exception:
        return type(None)


def PandasDataFrame():

    try:
        return sys.modules["pandas"].DataFrame
    except Exception:
        return type(None)


def PandasSeries():

    try:
        return sys.modules["pandas"].Series
    except Exception:
        return type(None)


def NumpyInt64():

    try:
        return sys.modules["numpy"].int64
    except Exception:
        return type(None)


def NumpyFloat64():

    try:
        return sys.modules["numpy"].float64
    except Exception:
        return type(None)


def NumpyFloat32():

    try:
        return sys.modules["numpy"].float32
    except Exception:
        return type(None)


def NumpyFloat16():

    try:
        return sys.modules["numpy"].float16
    except Exception:
        return type(None)


def NumpyInt8():

    try:
        return sys.modules["numpy"].int8
    except Exception:
        return type(None)


def NumpyArray():

    try:
        return sys.modules["numpy"].ndarray
    except Exception:
        return type(None)
