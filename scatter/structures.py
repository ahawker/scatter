"""
    scatter.structures
    ~~~~~~~~~~~~~~~~~~

    Implementations of useful, in-memory data structures.
"""
__all__ = ('Tree', 'Enum', 'ScatterDict', 'ScatterMapping')

import abc
import collections
import imp
import os
import sys

from scatter.importer import import_from


def immutable(func):
    """
    Decorate instance methods to define which can mutate an object instance.
    """

    def decorator(self, *args, **kwargs):
        raise TypeError('{0} is immutable'.format(self.__class__.__name__))

    return decorator


class ImmutableDict(dict):
    """
    Create a dictionary which is immutable after initial creation.
    """

    @immutable
    def setdefault(self, k, d=None):
        return super(ImmutableDict, self).setdefault(k, d)

    @immutable
    def update(self, E=None, **F):
        return super(ImmutableDict, self).update(E, **F)

    @immutable
    def pop(self, k, d=None):
        return super(ImmutableDict, self).pop(k, d)

    @immutable
    def popitem(self):
        return super(ImmutableDict, self).popitem()

    @immutable
    def __setitem__(self, key, value):
        return super(ImmutableDict, self).__setitem__(key, value)

    @immutable
    def __delitem__(self, key):
        return super(ImmutableDict, self).__delitem__(key)

    @immutable
    def clear(self):
        return super(ImmutableDict, self).clear()

    def copy(self):
        return ImmutableDict(self)

    def __copy__(self):
        return self


class KeyTransformMixin(object):
    """

    """

    @abc.abstractmethod
    def transform(self, key):
        raise NotImplementedError('Abstract method must be implemented in derived class.')


class LoadableMappingMixin(object):
    """

    """

    @abc.abstractmethod
    def filter(self, key):
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    def from_module(self, name):
        """
        Loads values from module which has already been imported.

        :param name: the name of the module to scan for configuration values
        """
        module = sys.modules.get(str(name))
        return self.from_object(module) if module else False

    def from_object(self, obj):
        """
        Populates self with values consumed from the given object.

        :param obj: the object to read in configuration values from
        """
        if obj is None:
            return False

        if isinstance(obj, basestring):
            obj = import_from(obj)

        if isinstance(obj, collections.Mapping):
            for k, v in obj.iteritems():
                if self.filter(k):
                    self[k] = v
        else:
            for k in dir(obj):
                if self.filter(k):
                    self[k] = getattr(obj, k)
        return True

    def from_env(self, name):
        """
        Loads data from an environment variable which contains the path to a file.

        :param name: the name of the environment variable
        """
        var = os.environ.get(name)
        if not var:
            raise RuntimeError('Environment variable {0} does not exist.'.format(name))
        return self.from_file(var)

    def from_file(self, path):
        """
        Loads data from a python file location at the given path.

        :param path: the path to a python file
        """
        if not path:
            return False
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        mod = imp.new_module('scatter_config')
        try:
            execfile(path, mod.__dict__)  # exec into module globals
        except IOError as e:
            e.strerror = 'Failed to load configuration file at {0}: {1}'.format(path, e.strerror)
            raise
        return self.from_object(mod)

    def from_args(self, args):
        """
        Loads data from an :class: `~argparse.Namespace` object.

        :param args: Namespace object from parsed command line arguments.
        """
        if args is None:
            return False
        return self.from_object(vars(args))


class ScatterMapping(collections.MutableMapping, KeyTransformMixin, LoadableMappingMixin):
    """

    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, mapping_cls, *args, **kwargs):
        self.store = mapping_cls()
        self.update(dict(*args, **kwargs))

    def __str__(self):
        return str(self.store)

    def __repr__(self):
        return repr(self.store)

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __contains__(self, item):
        return item in self.store

    def __getitem__(self, key):
        key = self.transform(key)
        return self.store[key]

    def __setitem__(self, key, value):
        key = self.transform(key)
        self.store[key] = value

    def __delitem__(self, key):
        key = self.transform(key)
        del self.store[key]

    def filter(self, key):
        return True

    def transform(self, key):
        return key

    def section(self, prefix='', sep='_'):
        """
        """
        section = prefix + sep
        return ScatterMapping(type(self.store),
                              ((k.strip(section), v) for k, v in self.iteritems() if k.startswith(prefix)))


class ScatterDict(ScatterMapping):
    """

    """

    def __init__(self, *args, **kwargs):
        super(ScatterDict, self).__init__(dict, *args, **kwargs)


class Tree(collections.defaultdict):
    """

    """

    @staticmethod
    def tree(*args, **kwargs):
        return Tree(tree, *args, **kwargs)

    def __getattr__(self, item):
        return self.get(item, tree())

    def __setattr__(self, key, value):
        self[key] = value
        return self

    def __delattr__(self, item):
        del self[item]
        return self


tree = Tree.tree


class Enum(object):
    """

    """

    def __init__(self, enum, names):
        for i, name in enumerate(names.split()):
            setattr(self, name, EnumMember(enum, name, 2 ** i))


class EnumMember(object):
    """

    """

    __slots__ = ('enum', 'name', 'value')

    def __init__(self, enum, name, value):
        self.enum = enum
        self.name = name
        self.value = value

    def __eq__(self, other):
        if isinstance(other, EnumMember):
            return self.value == other.value
        return self.value == other

    def __repr__(self):
        return '<{0}.{1}: {2}'.format(self.enum, self.name, self.value)

    def __str__(self):
        return '{0}.{1}'.format(self.enum, self.name)
