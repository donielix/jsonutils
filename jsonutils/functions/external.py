"""
We put here all references to third packages functions or methods
"""
import sys
from typing import Any

from jsonutils.functions.decorators import return_value_on_exception


@return_value_on_exception(False)
def isPandasNAN(instance: Any, fail_silently: bool = True) -> bool:

    import pandas as pd

    result = pd.isna(instance)
    if not isinstance(result, bool):
        return False
    return result


def DjangoQuerySet():

    try:
        from django.db.models import QuerySet

        return QuerySet
    except ImportError:
        return type(None)


def PandasDataFrame():

    try:
        from pandas import DataFrame

        return DataFrame
    except ImportError:
        return type(None)


def PandasSeries():

    try:
        from pandas import Series

        return Series
    except ImportError:
        return type(None)


def NumpyInt64():

    try:
        from numpy import int64

        return int64
    except ImportError:
        return type(None)


def NumpyFloat64():

    try:
        from numpy import float64

        return float64
    except ImportError:
        return type(None)


def NumpyFloat32():

    try:
        from numpy import float32

        return float32
    except ImportError:
        return type(None)


def NumpyFloat16():

    try:
        from numpy import float16

        return float16
    except ImportError:
        return type(None)


def NumpyInt8():

    try:
        from numpy import int8

        return int8
    except ImportError:
        return type(None)


def NumpyArray():

    try:
        from numpy import ndarray

        return ndarray
    except ImportError:
        return type(None)
