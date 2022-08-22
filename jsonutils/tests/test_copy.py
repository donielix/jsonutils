import unittest

from jsonutils.base import JSONObject
from jsonutils.query import All


class CopyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test1 = JSONObject(
            {
                "A": [
                    {"A": {"B": [1, 2]}, "B": "aa"},
                    {"B": "name", "C": None},
                ],
            }
        )

    def test_copy_whole_jsondict(self):
        test = self.test1
        test_copy = test.copy()
        self.assertDictEqual(test._data, test_copy._data)
        self.assertListEqual(test.A._data, test_copy.A._data)
        self.assertDictEqual(test.A._0._data, test_copy.A._0._data)
        self.assertEqual(test.A._1.C.jsonpath, test_copy.A._1.C.jsonpath)

    def test_copy_non_root(self):
        test = self.test1.A
        test_copy = test.copy()
        self.assertDictEqual(test.root._data, test_copy.root._data)

    def test_copy_queryset(self):
        query = self.test1.query(A=All)
        query_copy = query.copy()
        self.assertListEqual(query._data, query_copy._data)
