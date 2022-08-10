"""
We put here all references to third packages functions or methods
"""
import sys


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
