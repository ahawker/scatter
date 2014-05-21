"""
    tests.test_structures
    ~~~~~~~~~~~~~~~~~~~~~

    Implements tests for the :module: `~scatter.structures` module.
"""

import pytest

from scatter import structures


@pytest.fixture(scope='module')
def immutable_fixture():
    class ImmutableObject(object):
        @structures.immutable
        def immutable_function(self):
            assert False, 'Functions decorated as immutable should never be called!'

    return ImmutableObject()


@pytest.fixture(scope='module')
def immutable_dict_fixture():
    return structures.ImmutableDict(one=1, two=2, three=3)

@pytest.fixture(scope='module')
def scatter_mapping_fixture():
    return structures.ScatterMapping(dict, {
        'one': 1,
        'two': 2,
        'three': 3,
        'SECTION_NAME': 'section',
        'SECTION_VALUE': 'section_value'
    })


@pytest.fixture(scope='module')
def scatter_dict_fixture():
    return structures.ScatterDict({
        'one': 1,
        'two': 2,
        'three': 3,
        'SECTION_NAME': 'section',
        'SECTION_VALUE': 'section_value'
    })


@pytest.fixture(scope='function')
def tree_fixture():
    return structures.tree({
        'one': 1,
        'two': 2,
        'three': 3,
        'obj': object()
    })


@pytest.fixture(scope='module')
def enum_fixture():
    return structures.Enum('Fixture', 'One Two Three')


def test_immutable_raise(immutable_fixture):
    """
    Test that calling an `immutable` decorated function raises a `TypeError`.
    """
    with pytest.raises(TypeError):
        immutable_fixture.immutable_function()


def test_immutable_dict_raises_on_mutable_methods(immutable_dict_fixture):
    """
    Test that calling functions which normally mutate the data of a dictionary
    raises a `TypeError` when using a :class: `~scatter.structures.ImmutableDict` instance.
    """
    # dict.setdefault
    with pytest.raises(TypeError):
        immutable_dict_fixture.setdefault('four', 4)

    # dict.update
    with pytest.raises(TypeError):
        immutable_dict_fixture.update(four=4, five=5)

    # dict.pop
    with pytest.raises(TypeError):
        immutable_dict_fixture.pop('one', 1)

    # dict.popitem
    with pytest.raises(TypeError):
        immutable_dict_fixture.popitem()

    # dict.__setitem__
    with pytest.raises(TypeError):
        immutable_dict_fixture['four'] = 4

    # dict.__delitem__
    with pytest.raises(TypeError):
        del immutable_dict_fixture['one']

    # dict.clear
    with pytest.raises(TypeError):
        immutable_dict_fixture.clear()


def test_immutable_dict_returns_self_on_copy(immutable_dict_fixture):
    """
    Test that calls to copy a :class: `~scatter.structures.ImmutableDict` instance
    return the same instance and not a copy of itself.
    """
    #assert immutable_dict_fixture is immutable_dict_fixture.copy()
    #assert immutable_dict_fixture is immutable_dict_fixture.__copy__()


def test_scatter_mapping_section(scatter_mapping_fixture):
    """
    Test that calls to section a :class: `~scatter.structures.ScatterMapping` instance
    will section of a submapping
    """
    section = scatter_mapping_fixture.section('SECTION_')
    assert 'SECTION_NAME' in section
    assert 'SECTION_VALUE' in section


def test_scatter_mapping_filters_nothing(scatter_mapping_fixture):
    """
    Test that :class: `~scatter.structures.ScatterMapping` wont filter any loaded
    values.
    """
    assert scatter_mapping_fixture.filter(None) is True
    assert scatter_mapping_fixture.filter(0) is True
    assert scatter_mapping_fixture.filter(1) is True
    assert scatter_mapping_fixture.filter('Hello') is True
    assert scatter_mapping_fixture.filter([]) is True


def test_scatter_mapping_transforms_nothing(scatter_mapping_fixture):
    """
    Test that :class: `~scatter.structures.ScatterMapping` wont transform
    any of its given keys.
    """
    assert scatter_mapping_fixture.transform(None) is None
    assert scatter_mapping_fixture.transform(0) is 0
    assert scatter_mapping_fixture.transform(1) is 1
    assert scatter_mapping_fixture.transform('Hello') is 'Hello'
    #assert scatter_mapping_fixture.transform([]) is []


def test_scatter_mapping_from_object_import(scatter_mapping_fixture):
    """
    Test that :class: `~scatter.structures.ScatterMapping` will import and load
    attributes from a fully qualified type string.
    """


def test_scatter_mapping_from_object_mapping(scatter_mapping_fixture):
    """
    Test that :class: `~scatter.structures.ScatterMapping` will attempt to
    attach any key/value pairs from any `collections.Mapping` objects.
    """


def test_scatter_mapping_from_object_any(scatter_mapping_fixture):
    """
    Test that :class: `~scatter.structures.ScatterMapping` will attempt
    to attach any attributes from any object which is not of `collections.Mapping` type.
    """


def test_scatter_dict_filters_nothing(scatter_dict_fixture):
    """
    Test that :class: `~scatter.structures.ScatterDict` wont filter any
    loaded values.
    """
    assert scatter_dict_fixture.filter(None) is True
    assert scatter_dict_fixture.filter(0) is True
    assert scatter_dict_fixture.filter(1) is True
    assert scatter_dict_fixture.filter('Hello') is True
    assert scatter_dict_fixture.filter([]) is True


def test_scatter_dict_transforms_nothing(scatter_dict_fixture):
    """
    Test that :class: `~scatter.structures.ScatterDict` wont transform
    any of its given keys.
    """
    assert scatter_dict_fixture.transform(None) is None
    assert scatter_dict_fixture.transform(0) is 0
    assert scatter_dict_fixture.transform(1) is 1
    assert scatter_dict_fixture.transform('Hello') is 'Hello'
    #assert scatter_dict_fixture.transform([]) is []


def test_tree_setattr_into_mapping(tree_fixture):
    """
    Test that :class: `~scatter.structures.Tree` `__setattr__`
    sets the attribute value inside underlying mapping.
    """
    tree_fixture.name = 'tree'
    assert tree_fixture['name'] == 'tree'
    assert 'name' in tree_fixture


def test_tree_getattr_from_mapping(tree_fixture):
    """
    Test that :class: `~scatter.structures.Tree` `__getattr__`
    method acts as `__getitem__` and retrieves the identical value
    from the underlying mapping.
    """
    assert tree_fixture['one'] == 1
    assert tree_fixture.one == 1
    assert tree_fixture['obj'] is tree_fixture.obj


def test_tree_delattr_from_mapping(tree_fixture):
    """
    Test that :class: `~scatter.structures.Tree` `__delattr__`
    method acts as `__delitem__` and deletes the key from the
    underlying mapping.
    """
    del tree_fixture.one
    assert 'one' not in tree_fixture


def test_tree_default_is_tree(tree_fixture):
    """
    Test that :class: `~scatter.structures.Tree` returns
    a new :class: `~scatter.structures.Tree` instance when accessing
    keys which do not exist in the current hierarchy level.
    """
    assert 'default' not in tree_fixture
    assert isinstance(tree_fixture['default'], structures.Tree)
    assert isinstance(tree_fixture.default, structures.Tree)


def test_enum_member_attributes_set(enum_fixture):
    """
    Test that :class: `~scatter.structures.Enum` has instance
    attributes set for only the given initialization values.
    """
    assert hasattr(enum_fixture, 'One')
    assert hasattr(enum_fixture, 'Two')
    assert hasattr(enum_fixture, 'Three')
    assert not hasattr(enum_fixture, 'Four')


def test_enum_member_bit_flag_values(enum_fixture):
    """
    Test that :class: `~scatter.structures.Enum` sets
    each progressive member as a bit-flag (2^i) and that
    :class: `~scatter.structures.EnumMember` properly compare
    equality to `int` values.
    """
    assert enum_fixture.One == 2**0
    assert enum_fixture.Two == 2**1
    assert enum_fixture.Three == 2**2


@pytest.mark.parametrize('values', [None, True, 1, {}, ['One', 'Two']])
def test_enum_raises_on_invalid_input(values):
    """
    Test that :class: `~scatter.structures.Enum` raises exception
    on creation for all non-splittable types.
    """
    with pytest.raises(AttributeError):
        structures.Enum('Enum', values)