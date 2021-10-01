from jsonutils.base import JSONObject


def _validate_data(json_object, schema):
    # TODO implement this
    """
    Example of a schema
    {
        "type": Dict,
        "items": {
            "name": {
                "type": Str | Null,
                "contains": "a"
            },
            "team": {
                "type": ListDict | Null,
                "length": 2,
                "items": {
                    "name": {
                        "type": Str | Null
                    }
                    "age": {
                        "type": Int
                    }
                    "birth": {
                        "type": Datetime | Null
                    }
                }
            }
        }
    }
    """

    errors = []

    schema = JSONObject(schema)
