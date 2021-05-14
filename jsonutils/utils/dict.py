class Defaultdict(dict):
    def __init__(self, *args, default_value_=list(), **kwargs):
        super().__init__(*args, **kwargs)
        self.default_value = default_value_

    def __getitem__(self, key):
        if key not in self.keys():
            super().__setitem__(key, self.default_value)
            return self.default_value
        else:
            return super().__getitem__(key)
