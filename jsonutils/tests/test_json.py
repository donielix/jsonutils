import json
import unittest

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
    JSONPath,
    JSONSingleton,
    JSONStr,
)
from jsonutils.encoders import JSONObjectEncoder
from jsonutils.parsers import QuerySet


class JsonTest(unittest.TestCase):
    def setUp(self):
        self.test1 = JSONObject(
            [
                {"Float": 2.3, "Int": 1, "Str": "string"},
                {"Dict": {"Float": 0.0, "List": [1, 2, 3]}},
            ]
        )
        self.test2 = JSONObject(True)
        self.test3 = JSONObject(
            {"List": (True, False), "Bool": True, "Dict": {"Float": 3.2}}
        )
        self.test4 = JSONObject(
            {"List": [0, 0.1, "str", None], "Dict": {"Bool": True, "None": None}}
        )

        self.test5 = JSONObject(
            [
                {
                    "Float": 1.1,
                    "Dict": {
                        "List": [{"Str": "string1", "List": [None, True, False, 1]}],
                        "Null": None,
                    },
                },
                {
                    "List": [{"Dict": {"Float": "1.2"}, "Bool": True}],
                    "Dict": {"List": [None, {"Str": "string2"}]},
                },
                {"Datetime": "2021-05-01", "Dict": {"Datetime": "2021/06/01"}},
            ]
        )

        self.test6 = JSONObject(
            {
                "position_data": [
                    {"text": "dummy text 1", "pos": [1, 2]},
                    {"text": "dummy text 2", "pos": [3, 2]},
                    {"text": "dummy text 3", "pos": [1, 4]},
                    {"text": "dummy text 4", "pos": [2, 5]},
                    {"text": "dummy text 5", "pos": [4, 1]},
                ],
                "timestamp_data": [
                    {"value": 523687, "timestamp": "2021-05-01 08:00:00"},
                    {"value": 523689, "timestamp": "2021-05-01 09:00:00"},
                    {"value": 523787, "timestamp": "2021-05-02 08:30:00"},
                    {"value": 525687, "timestamp": "2021-05-05 18:00:25"},
                ],
            }
        )

        self.test7 = JSONObject(
            {
                "candidatos": [
                    {
                        "Nombre completo": "Fhànçaömá",
                        "Pasión": "Música",
                        "€uros": 356.3,
                    },
                    {"Nombre completo": "Üm€", "Pasión": "Comida", "€€": "28.36K €"},
                ]
            }
        )

    def test_types(self):
        """Assert all child types are the correct ones"""

        self.assertIsInstance(self.test1, JSONList)
        self.assertIsInstance(self.test1[0], JSONDict)
        self.assertIsInstance(self.test1[0]["Float"], JSONFloat)
        self.assertIsInstance(self.test1[0]["Int"], JSONInt)
        self.assertIsInstance(self.test1[0]["Str"], JSONStr)
        self.assertIsInstance(self.test1[1], JSONDict)
        self.assertIsInstance(self.test1[1]["Dict"], JSONDict)
        self.assertIsInstance(self.test1[1]["Dict"]["Float"], JSONFloat)
        self.assertIsInstance(self.test1[1]["Dict"]["List"], JSONList)

        self.assertIsInstance(self.test3, JSONDict)
        self.assertIsInstance(self.test3["List"], JSONList)
        self.assertIsInstance(self.test3["List"][0], JSONBool)
        self.assertIsInstance(self.test3["List"][1], JSONBool)
        self.assertIsInstance(self.test3["Bool"], JSONBool)
        self.assertIsInstance(self.test3["Dict"], JSONDict)
        self.assertIsInstance(self.test3["Dict"]["Float"], JSONFloat)

        self.assertIsInstance(self.test4, JSONDict)
        self.assertIsInstance(self.test4["List"], JSONList)
        self.assertIsInstance(self.test4["List"][0], JSONInt)
        self.assertIsInstance(self.test4["List"][1], JSONFloat)
        self.assertIsInstance(self.test4["List"][2], JSONStr)
        self.assertIsInstance(self.test4["List"][3], JSONNone)
        self.assertIsInstance(self.test4["Dict"], JSONDict)
        self.assertIsInstance(self.test4["Dict"]["Bool"], JSONBool)
        self.assertIsInstance(self.test4["Dict"]["None"], JSONNone)

    def test_keys(self):

        self.assertEqual(self.test1[0].key, None)
        self.assertEqual(self.test1[1].key, None)
        self.assertEqual(self.test1[0]["Float"].key, "Float")
        self.assertEqual(self.test1[0]["Int"].key, "Int")
        self.assertEqual(self.test1[0]["Str"].key, "Str")
        self.assertEqual(self.test1[1]["Dict"].key, "Dict")
        self.assertEqual(self.test1[1]["Dict"]["Float"].key, "Float")
        self.assertEqual(self.test1[1]["Dict"]["List"].key, "List")

    def test_parents(self):
        """Check every child object has the right parent object"""

        self.assertEqual(self.test1.parent, None)
        self.assertEqual(
            self.test1[0].parent,
            JSONList(
                [
                    {"Float": 2.3, "Int": 1, "Str": "string"},
                    {"Dict": {"Float": 0.0, "List": [1, 2, 3]}},
                ]
            ),
        )
        self.assertEqual(
            self.test1[1].parent,
            JSONList(
                [
                    {"Float": 2.3, "Int": 1, "Str": "string"},
                    {"Dict": {"Float": 0.0, "List": [1, 2, 3]}},
                ]
            ),
        )
        self.assertEqual(
            self.test1[0]["Float"].parent,
            JSONDict({"Float": 2.3, "Int": 1, "Str": "string"}),
        )
        self.assertEqual(
            self.test1[1]["Dict"].parent,
            JSONDict({"Dict": {"Float": 0.0, "List": [1, 2, 3]}}),
        )
        self.assertEqual(
            self.test1[1]["Dict"]["Float"].parent,
            JSONDict({"Float": 0.0, "List": [1, 2, 3]}),
        )
        self.assertEqual(
            self.test1[1]["Dict"]["List"].parent,
            JSONDict({"Float": 0.0, "List": [1, 2, 3]}),
        )
        self.assertEqual(
            self.test1[1]["Dict"]["List"][0].parent,
            JSONList([1, 2, 3]),
        )
        self.assertEqual(
            self.test1[1]["Dict"]["List"][1].parent,
            JSONList([1, 2, 3]),
        )

    def test_paths(self):

        self.assertEqual(
            self.test1.query(List__contains=2).first().jsonpath,
            JSONPath("1/Dict/List/"),
        )
        self.assertEqual(
            self.test1.query(List__contains=2).first().jsonpath.expr,
            '[1]["Dict"]["List"]',
        )

    def test_json_serializable(self):
        """Assert that the JSONObject is serializable"""

        self.assertEqual(
            json.dumps(self.test1).replace('"', "'"), self.test1.__repr__()
        )
        self.assertEqual(
            json.dumps(self.test2, cls=JSONObjectEncoder).replace('"', "'"),
            self.test2.__repr__().lower(),
        )
        self.assertEqual(
            json.dumps(self.test3, cls=JSONObjectEncoder).replace('"', "'"),
            self.test3.__repr__().replace("True", "true").replace("False", "false"),
        )

        self.assertEqual(
            json.dumps(self.test4, cls=JSONObjectEncoder),
            '{"List": [0, 0.1, "str", null], "Dict": {"Bool": true, "None": null}}',
        )

    def test_queries(self):

        self.assertEqual(self.test3.query(Bool="true"), [JSONBool(True)])
        self.assertEqual(
            self.test3.query(List__contains=True), [[JSONBool(True), JSONBool(False)]]
        )
        self.assertEqual(
            self.test1.query(Dict__contains=["Float", "List"]).last(),
            {"Float": 0.0, "List": [1, 2, 3]},
        )
        self.assertEqual(self.test5.query(Float=1.2), QuerySet([JSONStr(1.2)]))
        self.assertEqual(
            self.test5.query(Float__gt=1), QuerySet([JSONFloat(1.1), JSONStr(1.2)])
        )
        self.assertEqual(self.test5.query(Float__gt=2), QuerySet())
        self.assertEqual(self.test5.query(Str__exact="string2"), QuerySet(["string2"]))
        self.assertEqual(
            self.test5.query(List=[None, True, False, 1], include_parent_=True),
            [JSONDict({"Str": "string1", "List": [None, True, False, 1]})],
        )
        self.assertEqual(
            self.test5.query(Str__exact="string2", include_parent_=True),
            [{"Str": "string2"}],
        )
        self.assertEqual(
            self.test5.query(Datetime__gt="2021-05-01"), QuerySet(["2021/06/01"])
        )
        self.assertEqual(
            self.test5.query(Datetime__contains="2021-05"),
            QuerySet([JSONStr("2021-05-01")]),
        )
        self.assertEqual(
            self.test5.query(List__parent__contains="Str"),
            [
                {
                    "Str": "string1",
                    "List": [JSONNone(None), JSONBool(True), JSONBool(False), 1],
                }
            ],
        )
        self.assertEqual(
            self.test6.query(
                timestamp__gt="2021-05-01 08:30:00",
                timestamp__lte="2021-05-02 08:30:00",
                include_parent_=True,
            ),
            [
                {"value": 523689, "timestamp": "2021-05-01 09:00:00"},
                {"value": 523787, "timestamp": "2021-05-02 08:30:00"},
            ],
        )
        self.assertEqual(self.test6.query(pos__0__gte=2), [[3, 2], [2, 5], [4, 1]])
        # UNCOMMENT THIS WHEN IMPLEMENTED
        # self.assertEqual(
        #     self.test6.query(text__regex=r"(?:2|5)", pos__0__gte=2),
        #     [
        #         {"text": "dummy text 2", "pos": [3, 2]},
        #         {"text": "dummy text 5", "pos": [4, 1]},
        #     ],
        # )
