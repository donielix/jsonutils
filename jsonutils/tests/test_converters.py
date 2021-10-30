import unittest
from collections import deque
from unittest import skip
from jsonutils.base import JSONObject

from jsonutils.exceptions import JSONConvertException
from jsonutils.functions.converters import dict_to_list
from jsonutils.functions.seekers import _find_listable_dicts


class JsonTest(unittest.TestCase):
    def test_dict_to_list(self):
        self.assertListEqual(
            dict_to_list({0: True, 1: False, 2: True}), [True, False, True]
        )
        self.assertListEqual(dict_to_list({2: 2, 0: 0, 1: 1}), [0, 1, 2])
        self.assertListEqual(dict_to_list({0: [1, 2], 2: 0, 1: 1}), [[1, 2], 1, 0])

        self.assertRaisesRegex(
            JSONConvertException,
            "List items are not connected",
            lambda: dict_to_list({0: 0, 2: 2}),
        )
        self.assertRaisesRegex(
            JSONConvertException,
            "All dict's keys must be positive integers",
            lambda: dict_to_list({"0": 0, 2: 2}),
        )
        self.assertRaisesRegex(
            JSONConvertException,
            "All dict's keys must be positive integers",
            lambda: dict_to_list({0: 0, 1: 2, "A": 1}),
        )
        self.assertRaisesRegex(
            JSONConvertException,
            "All dict's keys must be positive integers",
            lambda: dict_to_list({-1: 0, 2: 2}),
        )
        self.assertRaisesRegex(
            JSONConvertException,
            "List have no 0th element defined",
            lambda: dict_to_list({1: 0, 2: 2}),
        )

    def test_listable_dicts(self):
        test = {"A": {"B": {0: 1, 1: 2}}}
        test2 = {"A": 1, "B": {0: 2, 1: {"A": True, "B": False}}}
        test3 = {"A": {0: {"A": {0: 1, 1: 2}}, 1: {"B": {0: 1, 1: {"A": 1, "B": 2}}}}}
        test4 = {
            "A": {
                "A": {
                    0: {
                        0: 1,
                        1: {0: {"A": {0: 1, 1: 2, 2: 3}}, 1: True},
                        2: {0: {"A": {0: True}}},
                    },
                    1: True,
                }
            },
            "B": {0: {"A": True, "B": {0: "A", 1: "B"}}},
        }

        test = _find_listable_dicts(test)
        self.assertDictEqual(test, {"A": {"B": [1, 2]}})

        test2 = _find_listable_dicts(test2)
        self.assertDictEqual(test2, {"A": 1, "B": [2, {"A": True, "B": False}]})

        test3 = _find_listable_dicts(test3)
        self.assertDictEqual(
            test3, {"A": [{"A": [1, 2]}, {"B": [1, {"A": 1, "B": 2}]}]}
        )

        test4 = _find_listable_dicts(test4)
        self.assertDictEqual(
            test4,
            {
                "A": {
                    "A": [[1, [{"A": [1, 2, 3]}, True], [{"A": [True]}]], True],
                },
                "B": [{"A": True, "B": ["A", "B"]}],
            },
        )
