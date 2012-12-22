class JSONWrapper(object):
    """
    A wrapper around JSON serialisable types to allow access to
    obj['key']['other'] as obj.key.other.

    A JSONWrapper behaves like its contained object in other respects.

    If the value needs to be stored and is a list or a dict, it is a good idea
    to store the return value from dict(wrapper) or list(wrapper) instead.
    """
    def __init__(self, d):
        self._d = d

        # Iterate over all attributes of the value
        for aname in dir(d):
            # Set all magic functions to proxy functions
            value = getattr(d, aname)
            if callable(value) \
                    and aname.startswith('__') and aname.endswith('__') \
                    and not aname in (
                        '__class__',
                        '__cmp__',
                        '__getattr__',
                        '__getitem__',
                        '__hash__'):
                setattr(self, aname,
                    lambda *args, **kwargs:
                        value(*args, **kwargs))

    def __cmp__(self, other):
        return cmp(self._d, other)

    def __getattr__(self, key):
        value = self._d[key]
        if isinstance(value, (dict, list)):
            return JSONWrapper(value)
        else:
            return value
    __getitem__ = __getattr__

    def __hash__(self):
        try:
            return self._d.__hash__()
        except AttributeError:
            return id(self._d)

    def __str__(self):
        return str(self._d)
