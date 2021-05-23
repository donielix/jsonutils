class UUIDdict(dict):
    """
    This objects represents a normal dict, but overwrites the way a new child item is set, asserting its UUID4 id is unique.
    """

    def __setitem__(self, key, child):

        while key in self.keys():
            key = child._set_new_uuid()

        return super().__setitem__(key, child)
    
