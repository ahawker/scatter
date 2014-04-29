"""
    scatter.descriptors
    ~~~~~~~~~~~~~~~~~~~

    Useful python descriptors.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('cached', 'MetaDescriptor')


import abc
import functools


class BaseDescriptor(object):
    """
    """

    @abc.abstractmethod
    def __get__(self, instance, owner=None):
        raise NotImplementedError('Abstract method must be implemented in derived class.')


class MetaDescriptor(BaseDescriptor):
    """
    """

    __name__ = None


class CachedProperty(BaseDescriptor):
    """
    """

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result

cached = CachedProperty
