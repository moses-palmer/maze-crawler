# coding: utf-8
# mazeweb
# Copyright (C) 2012-2014 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

class DictWrapper(dict):
    """A wrapper for :class:`dict` in configurations.

    This class allows accessing values using ``self.key``. If ``key`` is not in
    ``self``, and instance of :class:`NoneWrapper` is returned.

    Values can also be accessed by calling this instance thus:
    ``self('path.to.key', default_value)``.

    Values read using ``self.key`` and using calling are wrapped using
    :func:`wrap`.
    """
    def __getattr__(self, key):
        try:
            return wrap(self[key])
        except KeyError:
            return NoneWrapper()

    def __call__(self, path, default = None):
        v = self
        for part in path.split('.'):
            try:
                v = v[part]
            except KeyError:
                return wrap(default)
        return wrap(v)

class ListWrapper(list):
    """A wrapper for :class:`list` in configurations.

    When reading an index that does not exist, an instance of
    :class:`NoneWrapper` is returned.

    Values read using ``self[index]`` and ``for item in self`` are wrapped using
    :func:`wrap`.
    """
    def __getitem__(self, key):
        try:
            return wrap(super(ListWrapper, self).__getitem__(key))
        except IndexError:
            return NoneWrapper()

    def __iter__(self):
        for v in super(ListWrapper, self).__iter__():
            yield wrap(v)

class NoneWrapper(object):
    """A wrapper for missing values in configurations.

    When reading ``self.key`` or ``self[index]``, a new instance of NoneWrapper
    is returned.
    """
    def __getattr__(self, key):
        return NoneWrapper()
    __getitem__ = __getattr__
    __bool__ = __nonzero__ = lambda self: False


def wrap(v):
    """Wraps a primitive value.

    When called on an instance of :class:`dict`, this function will return a
    :class:`DictWrapper`.

    When called on an instance of :class:`list`, this function will return a
    :class:`ListWrapper`.

    When called on ``None``, this function will return a :class:`NoneWrapper`.

    :param v: The value to wrap.
    """
    if v is None:
        return NoneWrapper()
    elif isinstance(v, dict):
        return DictWrapper(v)
    elif isinstance(v, list):
        return ListWrapper(v)
    else:
        return v


def unwrap(v, default = None):
    """Unwraps a wrapped value.
    """
    if isinstance(v, NoneWrapper):
        return default
    elif isinstance(v, DictWrapper):
        return dict(v.items())
    elif isinstance(v, ListWrapper):
        return [unwrap(item) for item in v]
    else:
        return v


JSONWrapper = wrap

ConfigurationStore = DictWrapper
