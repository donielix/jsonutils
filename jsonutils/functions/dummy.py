import random

from jsonutils.base import (
    JSONBool,
    JSONDict,
    JSONFloat,
    JSONInt,
    JSONList,
    JSONNull,
    JSONStr,
)


def dummy_json(
    min_dict_length=2,
    max_dict_length=5,
    min_list_length=2,
    max_list_length=5,
    min_str_length=10,
    max_str_length=100,
):
    """
    Generate a dummy JSONObject instance
    """
    # TODO

    NODE_LIST_ALL = (
        JSONBool,
        JSONDict,
        JSONFloat,
        JSONInt,
        JSONList,
        JSONNull,
        JSONStr,
    )

    NODE_LIST_COMPOSED = (
        JSONDict,
        JSONList,
    )

    NODE_LIST_SINGLETON = (JSONStr, JSONFloat, JSONInt, JSONBool, JSONNull)

    COMPOSE_OBJECTS = []

    def get_random_node(kind="all"):
        if kind == "all":
            return random.choice(NODE_LIST_ALL)
        if kind == "composed":
            return random.choice(NODE_LIST_COMPOSED)
        if kind == "singleton":
            return random.choice(NODE_LIST_SINGLETON)
        else:
            raise ValueError(
                "Argument kind can only be some of the following: 'all', 'composed' or 'singletion'"
            )

    def fill_node(node):
        pass

    # get the initial node
    initial_node = get_random_node(kind="composed")

    return initial_node

