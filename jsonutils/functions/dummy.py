import random
import string

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

    # assert argument values are correct
    assert (
        min_dict_length <= max_dict_length
    ), "Argument min_dict_length must be less or equal than max_dict_length"

    assert (
        min_list_length <= max_list_length
    ), "Argument min_list_length must be less or equal than max_list_length"

    assert (
        min_str_length <= max_str_length
    ), "Argument min_str_length must be less or equal than max_str_length"

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

    def get_random_string(N=4):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=N))

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

    def initialize_singleton(node):
        "node must be a JSONSingleton instance"

        if node == JSONStr:
            return JSONStr("AAA")
        elif node == JSONBool:
            return JSONBool(True)
        elif node == JSONInt:
            return JSONInt(1)
        elif node == JSONFloat:
            return JSONFloat(3.8)
        elif node == JSONNull:
            return JSONNull(None)
        else:
            raise TypeError(f"node argument is not a JSONSingleton instance: {node}")

    def fill_composed_node(node):
        "node must be a JSONCompose instance"

        if isinstance(node, dict):
            length = random.randint(min_dict_length, max_dict_length)
            for _ in range(length):
                key = get_random_string()
                value = get_random_node()  # a node object
                if value.is_composed:
                    value = value()  # initialize composed object
                    COMPOSE_OBJECTS.append(value)
                else:
                    value = initialize_singleton(value)
                node.__setitem__(key, value)
        elif isinstance(node, list):
            length = random.randint(min_list_length, max_list_length)
            for _ in range(length):
                item = get_random_node()
                if item.is_composed:
                    item = item()
                    COMPOSE_OBJECTS.append(item)
                else:
                    item = initialize_singleton(item)
                node.append(item)

    # get the initial node
    initial_node = get_random_node(kind="composed")()

    fill_composed_node(initial_node)
    return initial_node
