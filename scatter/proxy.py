"""
    scatter.proxy
    ~~~~~~~~~~~~~

    Implements proxies to other objects.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('Proxy', 'ProxyService')

import service


class Proxy(object):
    """
    Proxy any object.

    Note: I'm pretty sure this could be generated programmatically at runtime.
    """

    __slots__ = ['__real__']

    def __init__(self, obj):
        object.__setattr__(self, '__real__', obj)

    @property
    def __dict__(self):
        return self.__real__.__dict__

    def __repr__(self):
        return repr(self.__real__)

    def __str__(self):
        return str(self.__real__)

    def __unicode__(self):
        return unicode(self.__real__)

    def __bool__(self):
        return bool(self.__real__)

    def __dir__(self):
        return dir(self.__real__)

    def __iter__(self):
        return iter(self.__real__)

    def __cmp__(self, other):
        return cmp(self.__real__, other)

    def __hash__(self):
        return hash(self.__real__)

    def __len__(self):
        return len(self.__real__)

    def __getattr__(self, item):
        return getattr(self.__real__, item)

    def __setattr__(self, key, value):
        return setattr(self.__real__, key, value)

    def __delattr__(self, item):
        return delattr(self.__real__, item)

    def __getitem__(self, item):
        return self.__real__[item]

    def __setitem__(self, key, value):
        self.__real__[key] = value

    def __delitem__(self, item):
        del self.__real__[item]

    def __getslice__(self, i, j):
        return self.__real__[i:j]

    def __setslice__(self, i, j, sequence):
        self.__real__[i:j] = sequence

    def __delslice__(self, i, j):
        del self.__real__[i:j]

    def __lt__(self, other):
        return self.__real__ < other

    def __le__(self, other):
        return self.__real__ <= other

    def __eq__(self, other):
        return self.__real__ == other

    def __ne__(self, other):
        return self.__real__ != other

    def __gt__(self, other):
        return self.__real__ > other

    def __ge__(self, other):
        return self.__real__ >= other

    def __call__(self, *args, **kwargs):
        return self.__real__(*args, **kwargs)

    def __contains__(self, item):
        return item in self.__real__

    def __add__(self, other):
        return self.__real__ + other

    def __sub__(self, other):
        return self.__real__ - other

    def __mul__(self, other):
        return self.__real__ * other

    def __div__(self, other):
        return self.__real__.__div__(other)

    def __truediv__(self, other):
        return self.__real__.__truediv__(other)

    def __floordiv__(self, other):
        return self.__real__ // other

    def __mod__(self, other):
        return self.__real__ % other

    def __divmod__(self, other):
        return self.__real__.__divmod__(other)

    def __pow__(self, power, modulo=None):
        return self.__real__ ** power

    def __lshift__(self, other):
        return self.__real__ << other

    def __rshift__(self, other):
        return self.__real__ >> other

    def __and__(self, other):
        return self.__real__ & other

    def __xor__(self, other):
        return self.__real__ ^ other

    def __or__(self, other):
        return self.__real__ | other

    def __neg__(self):
        return -self.__real__

    def __pos__(self):
        return +self.__real__

    def __abs__(self):
        return abs(self.__real__)

    def __invert__(self):
        return ~self.__real__

    def __complex__(self):
        return complex(self.__real__)

    def __int__(self):
        return int(self.__real__)

    def __long__(self):
        return long(self.__real__)

    def __float__(self):
        return float(self.__real__)

    def __oct__(self):
        return oct(self.__real__)

    def __hex__(self):
        return hex(self.__real__)

    def __index__(self):
        return self.__real__.__index__()

    def __coerce__(self, other):
        return self.__real__.__coerce__(other)

    def __enter__(self):
        return self.__real__.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.__real__.__exit__(exc_type, exc_val, exc_tb)

    def __radd__(self, other):
        return other + self.__real__

    def __rsub__(self, other):
        return other - self.__real__

    def __rmul__(self, other):
        return other * self.__real__

    def __rdiv__(self, other):
        return other / self.__real__

    def __rtruediv__(self, other):
        return self.__real__.__rtruediv__(other)

    def __rfloordiv__(self, other):
        return other // self.__real__

    def __rmod__(self, other):
        return other % self.__real__

    def __rdivmod__(self, other):
        return self.__real__.__rdivmod__(other)
