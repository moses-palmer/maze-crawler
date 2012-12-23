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


class ConfigurationStore(JSONWrapper):
    """
    A ConfigurationStore is a JSONWrapper that also supports to be called.

    The parameters when calling are described in __call__.
    """
    def __call__(self, path, default = None):
        """
        When calling a configuration store, a named configuration value is
        retrieved, or a default value if no value is stored.

        @param path
            The path to the configuration value. This is a list of names
            separated by '.'. The path is split on '.', and every part is used
            as key recursively from the configuration root to find the result.
        @param default
            The value to return if a part does not exist.
        @param TypeError if an item along the way does not support item['k']
        """
        v = self._d
        for part in path.split('.'):
            try:
                v = v[part]
            except KeyError:
                return default
        if isinstance(v, (list, dict)):
            return ConfigurationStore(v)
        else:
            return v
