import unittest
from unittest import skip

from jsonutils.base import JSONDict, JSONNode, JSONObject
from jsonutils.exceptions import JSONPathException


class JsonTest(unittest.TestCase):
    def test_dict_builds(self):
        path1 = [(("A", "B"), True), (("A", "C"), False)]
        path2 = [(("A",), 1), (("A", "B"), 1)]  # incompatible paths
        path3 = [
            (("A",), 1),
            (("B", 0), 2),
            (("B", 1, "A"), True),
            (("B", 1, "B"), False),
        ]
        path4 = [(("A", 0), 1), (("A", 2), 2)]  # not a connected list
        path5 = [(("A",), 1), ((0,), 1)]  # incompatible

        self.assertDictEqual(
            JSONObject.from_path(path1), {"A": {"B": True, "C": False}}
        )

        self.assertIsInstance(JSONObject.from_path(path1), JSONNode)

        self.assertDictEqual(
            JSONObject.from_path(path3), {"A": 1, "B": [2, {"A": True, "B": False}]}
        )

        self.assertRaisesRegex(
            JSONPathException,
            "node structure is incompatible",
            lambda: JSONObject.from_path(path2),
        )
        self.assertRaisesRegex(
            JSONPathException,
            "node structure is incompatible",
            lambda: JSONObject.from_path(path4),
        )
        self.assertRaisesRegex(
            JSONPathException,
            "node structure is incompatible",
            lambda: JSONObject.from_path(path5),
        )
    @skip
    def test_list_builds(self):
        path1 = [
            ((0, "A"), 1),
            ((0, "B"), 2),
            ((1, "C"), 3),
            ((1, "D"), 4),
        ]
        self.assertListEqual(
            JSONObject.from_path(path1), [{"A": 1, "B": 2}, {"C": 3, "D": 4}]
        )
