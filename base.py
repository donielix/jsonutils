# This module contains the base objects needed
class JSONObject:
    """
    This class acts as a switcher. It will return the corresponding class instance for a given data.
    """

    def __new__(cls, data):

        if isinstance(data, dict):
            return JSONDict(data)
        elif isinstance(data, list):
            return JSONList(data)
        elif isinstance(data, bool):
            return JSONBool(data)
        elif isinstance(data, str):
            return JSONStr(data)
        elif isinstance(data, float):
            return JSONFloat(data)
        elif isinstance(data, int):
            return JSONInt(data)
        else:
            raise TypeError(f"Wrong data's format: {type(data)}")


class JSONMaster:
    """
    This is the base class for all JSON objects.

    Attributes:
    -----------
        _child_objects:
        key: last dict parent key where the object comes from
        index: las list parent index where the object comes from
    """

    def __init__(self, *args, **kwargs):

        self._child_objects = []
        self.key = None
        self.index = None


class JSONCompose(JSONMaster):
    """
    This is the base class for JSON composed objects.
    Composed objects can be dict or list instances.
    Composed objects can send queries to childs.
    """

    is_composed = True

    def __init__(self, *args, **kwargs):
        """
        By initializing instance, it assign types to child items
        """
        super().__init__(*args, **kwargs)
        self._assign_childs()

    def _assign_childs(self):

        if isinstance(self, JSONDict):
            for key, value in self.items():
                child = JSONObject(value)
                child.key = key
                self.__setitem__(key, child)
                self._child_objects.append(child)

        elif isinstance(self, JSONList):
            for index, item in enumerate(self):
                child = JSONObject(item)
                child.index = index
                self.__setitem__(index, child)
                self._child_objects.append(child)

    def query(self, **q):

        childs = self._child_objects
        for child in childs:
            # do some stuff
            print(f"Objeto: {child}\t Key: {child.key}\t Idx: {child.index}")
            if child.is_composed:
                child.query(**q)


class JSONSingleton(JSONMaster):
    """
    This is the base class for JSON singleton objects
    """

    is_composed = False

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)


class JSONDict(dict, JSONCompose):
    """"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        JSONCompose.__init__(self, *args, **kwargs)


class JSONList(list, JSONCompose):
    """"""

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        JSONCompose.__init__(self, *args, **kwargs)


class JSONStr(str, JSONSingleton):
    pass


class JSONFloat(float, JSONSingleton):
    pass


class JSONInt(int, JSONSingleton):
    pass


class JSONBool(JSONSingleton):
    def __init__(self, data):

        if not isinstance(data, bool):
            raise TypeError(f"Argument is not a valid boolean type: {type(data)}")
        super().__init__()
        self._data = data

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self._data)

    def __bool__(self):
        return self._data
