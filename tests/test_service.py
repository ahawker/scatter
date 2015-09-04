"""
    tests.test_service
    ~~~~~~~~~~~~~~~~~~

    Implements tests for the :class: `~scatter.service.Service` class.
"""

import pytest

from scatter.meta import resolve_type
from scatter.service import Service, ServiceState


@pytest.fixture(scope='function')
def service(request):
    s = Service()
    s.init(config=dict(TESTING=True))
    return s


def test_service_defaults(service):
    """
    """
    assert service.name == service.__class__.__name__
    assert service.type == service.__class__.__name__
    assert service.fully_qualified_type == resolve_type(service)


def test_service_name(service):
    """
    """
    assert service.name == service.__class__.__name__


def test_service_meta_registers_new_types():
    """

    """


def test_service_meta_caches_types():
    """

    """