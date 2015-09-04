"""
    scatter.utils
    ~~~~~~~~~~~~~

    Dumping grounds for general utility/helper functions who have no better home.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('iterable', 'get_import_path')


import os
import sys
import collections


def iterable(item):
    """
    Return an iterable which contains the given item.
    """
    if isinstance(item, collections.Iterable) and not isinstance(item, basestring):
        return item
    return (item,) if item is not None else ()


def get_import_path(import_name):
    """
    Get the full local file path for the given import name.

    :param import_name: Name of module import we're finding local path of.
    """
    # Module has already been loaded.
    module = sys.modules.get(import_name)
    if module is not None and hasattr(module, '__file__'):
        return os.path.dirname(os.path.abspath(module.__file__))

    # Check the package loader.
    import pkgutil

    loader = pkgutil.get_loader(import_name)
    if loader is None or import_name == '__main__':
        return os.getcwd()

    # Attempt to import the module and return path to it.
    import_path = loader.get_filename(import_name)
    return os.path.dirname(os.path.abspath(import_path))
