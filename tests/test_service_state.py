"""
    tests.test_service_state
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Implements tests for the :class: `~scatter.service.ServiceStateMachine` class.
"""

import pytest

from scatter.service import Service, ServiceStateMachine


@pytest.fixture(scope='function')
def service(request):
    s = Service()
    s.init(config=dict(TESTING=True))
    return s


def test_service_state_transitions(service):
    """
    Test top-level service "action" methods actually change the
    underlying state of the service and its state machine.
    """
    assert service.state_machine.is_initialized

    service.start()
    assert service.state_machine.is_running

    service.stop()
    assert service.state_machine.is_stopped