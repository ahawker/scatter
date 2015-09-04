"""
    scatter.registry
    ~~~~~~~~~~~~~~~~

    Implements service type registry for maintaining extensions.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.

"""
__all__ = ('Registry',)


import weakref

from scatter.importer import PackageImporter
from scatter.meta import is_abstract
from scatter.structures import ScatterMapping
from scatter.exceptions import ScatterException


class RegistryError(ScatterException):
    """
    """


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
        try:
            del self[key]
        except KeyError:
            raise RegistryError('Entry {0} not found'.format(key))

    def get_concrete_types(self, abc):
        """
        Return collection of service classes which implement the given abstract class.

        :param abc: Class object which defines an abstract `scatter.service.Service` definition.
        """
        return (c for c in self.values() if issubclass(c, abc) and not is_abstract(c))

    def get_concrete_type(self, abc, silent=False):
        """
        Return a service class which implements the given abstract class.

        :param abc: Class object which defines an abstract `scatter.service.Service` definition.
        :param silent: Boolean flag to set if we should raise a `ServiceDependencyError` or return None
        when no types implementing the given abstract type are found.
        """
        cls = next((c for c in self.values() if issubclass(c, abc) and not is_abstract(c)), None)
        if cls is not None:
            return cls

        if not silent:
            msg = ('No implementation found for abstract class "{0}". '
                   'If attempting to load an implementation defined as an extension, '
                   'please note that extension modules must be explicitly imported before doing so.').format(abc)
            raise RegistryError(msg)


global_registry = Registry()