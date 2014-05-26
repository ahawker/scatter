"""
    tests/test_registry
    ~~~~~~~~~~~~~~~~~~~

    Implements tests for the :module: `scatter.registry` module.
"""

import pytest

from scatter.meta import resolve_type
from scatter.registry import Registry, RegistryError
from scatter.service import Service


@pytest.fixture(scope='module')
def abstract_service():
    class AbstractType(Service):
        __abstract__ = True

    return AbstractType

@pytest.fixture(scope='module')
def service(abstract_service):
    class ServiceType(abstract_service):
        pass

    return resolve_type(ServiceType), ServiceType


@pytest.fixture(scope='module')
def unregistered_service():
    class UnregisteredService(object):
        pass

    return resolve_type(UnregisteredService), UnregisteredService


@pytest.fixture(scope='function')
def registry(service):
    r = Registry()
    r.register(*service)
    return r


def test_registry_register(registry, service):
    """
    Test that `registry.register` stores the class instance.
    """
    fully_qualified_type, cls = service
    assert fully_qualified_type in registry
    assert registry[fully_qualified_type] == cls
    assert registry[fully_qualified_type] is cls


def test_registry_deregister_found(registry, service):
    """
    Test that `registry.deregister` removes the stored class instance
    when a match is found.
    """
    fully_qualified_type, cls = service
    assert fully_qualified_type in registry
    registry.deregister(fully_qualified_type)
    assert fully_qualified_type not in registry


def test_registry_deregister_not_found(registry, unregistered_service):
    """
    Test that `registry.deregister` raises when attempting to remove
    a class instance which isn't found.
    """
    fully_qualified_type, cls = unregistered_service
    assert fully_qualified_type not in registry
    with pytest.raises(RegistryError):
        registry.deregister(fully_qualified_type)


def test_registry_concrete_type_found(registry, service):
    """
    Test that `registry.get_concrete_type` returns the found
    class instance match.
    """
    fully_qualified_type, cls = service
    concrete = registry.get_concrete_type(cls)
    assert concrete is cls


def test_registry_concrete_type_found_subclass(registry, abstract_service, service):
    """
    Test that `registry.get_concrete_type` returns subclass instance
    when the target class is marked abstract.
    """
    fully_qualified_type, cls = service
    concrete = registry.get_concrete_type(abstract_service)
    assert concrete is cls


def test_registry_concrete_type_not_found(registry, unregistered_service):
    """
    Test that `registry.get_concrete_type` raises when
    no matches exist.
    """
    fully_qualified_type, cls = unregistered_service
    with pytest.raises(RegistryError):
        registry.get_concrete_type(cls)


def test_registry_concrete_type_not_found_silent(registry, unregistered_service):
    """
    Test that `registry.get_concrete_type` returns `None`
    when no matches exist and silent is `True`.
    """
    fully_qualified_type, cls = unregistered_service
    concrete = registry.get_concrete_type(cls, silent=True)
    assert concrete is None