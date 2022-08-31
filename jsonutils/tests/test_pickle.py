import pickle
from unittest import TestCase, skip

from jsonutils import JSONObject
from jsonutils.base import JSONNull


class TestPickleObjects(TestCase):
    def setUp(self) -> None:
        self.test = JSONObject(
            dict(null=None, float=1.2, int=1, obj=dict(A=1), arr=[1, 2], str="aa")
        )

    @skip
    def test_json_null_pickable(self):
        # TODO add __setstate__ and __getstate__ to nodes
        original_obj = JSONNull(None)
        pick = pickle.dumps(original_obj)
        obj = pickle.loads(pick)
        self.assertEqual(original_obj, obj)
