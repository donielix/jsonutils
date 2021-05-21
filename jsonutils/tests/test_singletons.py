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
    JSONMaster,
    JSONNone,
    JSONObject,
    JSONSingleton,
    JSONStr,
)
from jsonutils.encoders import JSONObjectEncoder
from jsonutils.functions.parsers import QuerySet


class JsonTest(unittest.TestCase):
    def test_jsonstr(self):
        self.assertEqual(
            JSONStr(" - $4,312,555.52  ").to_float(), JSONFloat(-4312555.52)
        )
        self.assertEqual(
            JSONStr(" + $4,312,555.520  ").to_float(), JSONFloat(4312555.52)
        )
        self.assertEqual(JSONStr("2021-01-04").to_datetime(), datetime(2021, 1, 4))
        self.assertEqual(JSONStr("2021/01/04").to_datetime(), datetime(2021, 1, 4))
        self.assertEqual(JSONStr("01-02-2021").to_datetime(), datetime(2021, 2, 1))
        self.assertEqual(JSONStr("01/02/2021").to_datetime(), datetime(2021, 2, 1))
        self.assertGreater(JSONStr(" -$ 2,132.01US"), -5000)
        self.assertLess(JSONStr(" -5€ "), -4)
