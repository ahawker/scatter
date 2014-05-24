"""
    tests.test_module
    ~~~~~~~~~~~~~~~~

    Implements tests for the :module: `scatter.importer` module.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""

import inspect
import pytest
import sys

from scatter.importer import import_from, _is_module_in_traceback


@pytest.fixture(scope='module', params=['Foo', 'Bar'])
def cls_fixture(request):
    return type(request.param, (object,), {})


def test_import_from_class_object(cls_fixture):
    """
    Test that `import_from` will return the identical class object
    if given one.
    """
    assert import_from(cls_fixture) is cls_fixture


@pytest.mark.parametrize('module', ['pytest', 'scatter.importer', 'os.path', 'multiprocessing.process'])
def test_import_from_module_path(module):
    """
    Test that `import_from` will return the module instance stored in `sys.modules`
    for a importable module.
    """
    imported = import_from(module)
    assert inspect.ismodule(imported)
    assert imported is sys.modules[module]
    assert imported == sys.modules[module]


@pytest.mark.parametrize('module', ['foo', 'bar', 'os.path.foo', 'sys.bar'])
def test_import_from_invalid_module_raises(module):
    """
    Test that `import_from` will raise an `ImportError` when importing
    a module path which doesn't exist.
    """
    with pytest.raises(ImportError):
        import_from(module)


@pytest.mark.parametrize('module', ['foo', 'bar', 'os.path.foo', 'sys.bar'])
def test_import_from_invalid_module_silent(module):
    """
    Test that `import_from` will consume an `ImportError` and return
    `None` when importing a module path which doesn't exist
    and the `silent` parameter is `True`.
    """
    assert import_from(module, silent=True) is None


@pytest.mark.parametrize('cls', ['collections.OrderedDict', 'threading.Thread', 'scatter.importer.ExtensionImporter'])
def test_import_from_class_path(cls):
    """
    Test that `import_from` will return a class object when importing
    a valid class path string.
    """
    imported = import_from(cls)
    assert inspect.isclass(imported)


@pytest.mark.parametrize('cls', ['threading.ThreadFoo', 'multiprocessing.DatProcess', 'os.NotAClass'])
def test_import_from_invalid_class_raises(cls):
    """
    Test that `import_from` will raise an `ImportError` when importing
    a class path which doesn't exist.
    """
    with pytest.raises(ImportError):
        import_from(cls)


@pytest.mark.parametrize('cls', ['threading.ThreadFoo', 'multiprocessing.DatProcess', 'os.NotAClass'])
def test_import_from_invalid_class_silent(cls):
    """
    Test that `import_from` will consume an `ImportError` and return
    `None` when importing a class path which doesn't exist and the
    `silent` parameter is `True`.
    """
    assert import_from(cls, silent=True) is None


@pytest.mark.parametrize('func', ['scatter.importer.import_from', 'os.path.join', 'threading.current_thread'])
def test_import_from_func_path(func):
    """
    Test that `import_from` will return a function object when importing
    a valid function path string.
    """
    imported = import_from(func)
    assert inspect.isfunction(imported)


@pytest.mark.parametrize('func', ['os.path.getsandwich', 'scatter.get_foobar', 'sys.getsyscolor'])
def test_import_from_invalid_func_raises(func):
    """
    Test that `import_from` will raise an `ImportError` when importing
    a function path which doesn't exist.
    """
    with pytest.raises(ImportError):
        import_from(func)


@pytest.mark.parametrize('func', ['os.path.getsandwich', 'scatter.get_foobar', 'sys.getsyscolor'])
def test_import_from_invalid_func_silent(func):
    """
    Test that `import_from` will consume an `ImportError` and return
    `None` when importing a function path which doesn't exist and the
    `silent` parameter is `True`.
    """
    assert import_from(func, silent=True) is None


@pytest.mark.parametrize('module', ['tests.test_importer', pytest.mark.xfail('tests'), pytest.mark.xfail('tests.foo')])
def test_module_found_in_traceback(module):
    """
    Test that `_is_module_in_traceback` returns `True` when the given
    module or package name is within the raised traceback.
    """
    try:
        raise ImportError('See you in hell, candy boys!')
    except ImportError:
        exc_type, exc_value, traceback = sys.exc_info()
        assert _is_module_in_traceback(module, traceback)