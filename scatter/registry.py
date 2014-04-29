"""
    scatter.registry
    ~~~~~~~~~~~~~~~~

    Implements service type registry for maintaining extensions.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.

"""
__all__ = ('Registry',)


import weakref

from scatter.structures import ScatterMapping
from scatter.exceptions import ServiceDependencyError


class Entry(object):
    """

    """


class Registry(ScatterMapping):
    """

    """

    def __init__(self):
        super(Registry, self).__init__(weakref.WeakValueDictionary)

    def register(self, key, service):
        """

        :param service:
        :return:
        """
        self[key] = service

    def deregister(self, key):
        """

        :param name:
        :return:
        """
        del self[key]

    def get_concrete_type(self, abc, silent=False):
        """
        Return a service class which implements the given abstract class.

        :param abc: Class object which defines an abstract `scatter.service.Service` definition.
        :param silent: Boolean flag to set if we should raise a `ServiceDependencyError` or return None
        when no types implementing the given abstract type are found.
        """
        cls = next((c for c in self.values() if issubclass(c, abc) and not c.is_abstract()), None)
        if cls is not None:
            return cls

        if not silent:
            msg = ('No implementation found for abstract service class "{0}". '
                   'If attempting to load an implementation defined as an extension, '
                   'please note that extension modules must be explicitly imported before doing so.').format(abc)
            raise ServiceDependencyError(msg)


global_registry = Registry()