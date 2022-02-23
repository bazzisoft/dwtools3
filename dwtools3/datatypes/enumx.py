"""
Extensions to the built-in Python 3.4 Enum class.

Supports regular key-value enumerations as well as ordered
enumerations for SQL sortability. Each enum has a ``name``
(the python variable name), a ``key`` (string key if provided,
or string of the python variable name) and a ``value``.

Supports comparisons made on the ``key``.

Provides extra methods to list the enumerations or its keys.

Usage
-----
::

    class Regular(EnumX):
        ONE = 'One'
        TWO = 'Two'


    class SQLSortable(EnumX):
        ONE = ('10-ONE', 'One')
        TWO = ('20-TWO', 'Two')


    >>> SQLSortable.ONE.name
    'ONE'

    >>> SQLSortable.ONE.key
    '10-ONE'

    >>> SQLSortable.ONE.value
    'One'

    >>> str(SQLSortable.ONE)
    '10-ONE'

    >>> Regular.all()
    # Returns an iterable of key-value tuples

    >>> Regular.as_dict()
    # Returns a dict of key-value pairs

    >>> Regular.keys()
    # Returns an iterable of keys

    >>> Regular.from_key(k)
    # Returns the enum instance for the given string key
"""
import enum
import itertools
import operator
from collections import OrderedDict


class EnumX(enum.Enum):
    def __init__(self, *values):
        if len(values) == 1:
            self.key = self.name
        else:
            self.key = values[0]
            self._value_ = values[1] if len(values) == 2 else values[1:]

    def as_tuple(self):
        """
        Returns the key-value pair of this enum instance.
        """
        return (self.key, self.value)

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return self.key

    def _cmp(self, other, op):
        if self.__class__ is other.__class__:
            return op(self.key, other.key)
        else:
            return op(self.key, other)

    def __eq__(self, other):
        return self._cmp(other, operator.eq)

    def __ne__(self, other):
        return self._cmp(other, operator.ne)

    def __gt__(self, other):
        return self._cmp(other, operator.gt)

    def __ge__(self, other):
        return self._cmp(other, operator.ge)

    def __lt__(self, other):
        return self._cmp(other, operator.lt)

    def __le__(self, other):
        return self._cmp(other, operator.le)

    @classmethod
    def _get_key_cache(cls):
        if not hasattr(cls, '_key_cache'):
            setattr(cls, '_key_cache', OrderedDict((e.key, e) for e in cls))
        return cls._key_cache

    @classmethod
    def all(cls):
        """
        Returns all key-label pairs as an iterator of tuples.

        Useful to pass on to a Django field as the possible choices.
        """
        return (e.as_tuple() for e in cls)

    @classmethod
    def all_before(cls, key):
        """
        Returns an iterable of all keys of this enumeration before the specified key.
        """
        return itertools.takewhile(lambda x: x[0] != key, cls.all())

    @classmethod
    def all_from(cls, key):
        """
        Returns an iterable of all keys of this enumeration including and after the specified key.
        """
        return itertools.dropwhile(lambda x: x[0] != key, cls.all())

    @classmethod
    def as_dict(cls):
        """
        Returns the key-label pairs of the enumeration as a dict.
        """
        return dict(cls.all())

    @classmethod
    def keys(cls):
        """
        Returns an iterable of all keys of this enumeration.
        """
        return (e.key for e in cls)

    @classmethod
    def keys_before(cls, key):
        """
        Returns an iterable of all keys of this enumeration before the specified key.
        """
        return itertools.takewhile(lambda x: x != key, cls.keys())

    @classmethod
    def keys_from(cls, key):
        """
        Returns an iterable of all keys of this enumeration including and after the specified key.
        """
        return itertools.dropwhile(lambda x: x != key, cls.keys())

    @classmethod
    def max_length(cls):
        """
        Calculates the maximum length of the key.

        You can set the ``max_length`` value of a ``CharField``
        to the result of this method.
        """
        value = max(cls.keys(), key=len)
        return 1 if not value else len(value)

    @classmethod
    def from_key(cls, key):
        """
        Returns the enum instance for the given string key.
        """
        keymap = cls._get_key_cache()
        try:
            return keymap[key]
        except KeyError:
            raise KeyError('Key "{}" not found in enum "{}"'.format(key, cls.__name__)) from None
