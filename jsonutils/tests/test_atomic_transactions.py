import unittest

from jsonutils.base import JSONObject
from jsonutils.query import All


class AtomicTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test1 = JSONObject(
            {
                "A": [
                    {"A": {"B": [1, 2]}, "B": "aa"},
                    {"B": "name", "C": None},
                ],
            }
        )
    def test_atomic_update(self):
        test = self.test1
        test_copy = test.copy()
        with self.assertRaises(Exception):
            test.query(A=All).update(1, atomic=True)
        self.assertDictEqual(test._data, test_copy._data)

    def test_atomic_delete(self):
        test = self.test1
        test_copy = test.copy()
        with self.assertRaises(Exception):
            test.query(A=All).delete(1, atomic=True)
        self.assertDictEqual(test._data, test_copy._data)