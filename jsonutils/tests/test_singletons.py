import json
import unittest
from datetime import datetime

from jsonutils.base import (
    JSONBool,
    JSONCompose,
    JSONDict,
    JSONFloat,
    JSONInt,
    JSONList,
    JSONNode,
    JSONNull,
    JSONObject,
    JSONSingleton,
    JSONStr,
)
from jsonutils.encoders import JSONObjectEncoder
from jsonutils.query import QuerySet


class JsonTest(unittest.TestCase):
    def test_jsonstr(self):
        self.assertEqual(
            JSONStr(" - $4,312,555.52  ").to_float(), JSONFloat(-4312555.52)
        )
        self.assertEqual(
            JSONStr(" + $4,312,555.520  ").to_float(), JSONFloat(4312555.52)
        )
        self.assertEqual(JSONStr(" 2021-01-04").to_datetime(), datetime(2021, 1, 4))
        self.assertEqual(JSONStr(" 2021/01/04 ").to_datetime(), datetime(2021, 1, 4))
        self.assertEqual(JSONStr("01-02-2021").to_datetime(), datetime(2021, 2, 1))
        self.assertEqual(JSONStr("01/02/2021 ").to_datetime(), datetime(2021, 2, 1))
        self.assertEqual(
            JSONStr("01/02/2021 T 09:00:30").to_datetime(),
            datetime(2021, 2, 1, 9, 0, 30),
        )
        self.assertEqual(
            JSONStr("01/02/2021 T 09:00:30.0054").to_datetime(),
            datetime(2021, 2, 1, 9, 0, 30),
        )
        self.assertEqual(
            JSONStr("01/02/2021 T09.00.30.0054Z").to_datetime(),
            datetime(2021, 2, 1, 9, 0, 30),
        )
        self.assertEqual(
            JSONStr(" 01/02/2021T 09.00.30.0054Z ").to_datetime(),
            datetime(2021, 2, 1, 9, 0, 30),
        )
        self.assertGreater(JSONStr(" -$ 2,132.01US"), -5000)
        self.assertLess(JSONStr(" -5€ "), -4)
