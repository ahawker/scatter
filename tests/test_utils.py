"""
    test.test_utils
    ~~~~~~~~~~~~~~~

    Implements tests for the :module: `~scatter.utils` module.
"""

import collections
import pytest

from scatter.utils import iterable, get_import_path


@pytest.fixture(scope='module')
def tuple_fixture():
    return 1, 2, 3


@pytest.fixture(scope='module')
def list_fixture():
    return [1, 2, 3]


@pytest.fixture(scope='module')
def class_fixture(tuple_fixture):
    class IterableClass(object):
        def __iter__(self):
            return iter(tuple_fixture)

    return IterableClass()


@pytest.fixture(scope='module')
def invalid_class_fixture():
    class InvalidIterableClass(object):
        pass

    return InvalidIterableClass()


@pytest.fixture(scope='module')
def dict_fixture():
    return dict(one=1, two=2, three=3)


@pytest.fixture(scope='module')
def set_fixture():
    return {1, 2, 3}


@pytest.fixture(scope='module')
def str_fixture():
    return str('Hello World')


@pytest.fixture(scope='module')
def unicode_fixture():
    return unicode('Hello World')


def test_iterable_tuple_unchanged(tuple_fixture):
    """
    Test that when `iterable` is given a `tuple`, the identical tuple is returned.
    """
    assert tuple_fixture is iterable(tuple_fixture)


def test_iterable_list_unchanged(list_fixture):
    """
    Test that when `iterable` is given a `list`, the identical list is returned.
    """
    assert list_fixture is iterable(list_fixture)


def test_iterable_dict_unchanged(dict_fixture):
    """
    Test that when `iterable` is given a `dict`, the identical dict is returned.
    """
    assert dict_fixture is iterable(dict_fixture)


def test_iterable_set_unchanged(set_fixture):
    """
    Test that when `iterable` is given a `set`, the identical set is returned.
    """
    assert set_fixture is iterable(set_fixture)


def test_iterable_class_iter_unchanged(class_fixture):
    """
    Test that when `iterable` is given a class which defines __iter__, the identical
    class instance is returned.
    """
    assert class_fixture is iterable(class_fixture)


def test_iterable_class_invalid_to_tuple(invalid_class_fixture):
    """
    Test that when `iterable` is given a class which doesn't define __iter__, an iterable
    containing the class instance is returned.
    """
    i = iterable(invalid_class_fixture)
    assert invalid_class_fixture is not i
    assert isinstance(i, collections.Iterable)


def test_iterable_string_to_tuple(str_fixture):
    """
    Test that when `iterable` is given a `str`, a tuple containing the string is returned.
    """
    i = iterable(str_fixture)
    assert str_fixture is not i
    assert isinstance(i, collections.Iterable)


def test_iterable_unicode_to_tuple(unicode_fixture):
    """
    Test that when `iterable` is given a `unicode`, a tuple containing the unicode is returned.
    """
    i = iterable(unicode_fixture)
    assert unicode_fixture is not i
    assert isinstance(i, collections.Iterable)
