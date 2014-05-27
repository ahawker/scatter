"""
    tests.test_state
    ~~~~~~~~~~~~~~~~

    Implements tests for the `scatter.state` module.
"""

import pytest

from scatter.state import StateMachine, transition, guard, InvalidTransition


@pytest.fixture(scope='function', params=['off'])
def switch_state_machine(request):
    return SwitchStateMachine(request.param)


@pytest.fixture(scope='function')
def switch(switch_state_machine):
    return Switch(switch_state_machine)


class SwitchStateMachine(StateMachine):
    """
    State machine for a switch which has two states: on and off.
    """

    @transition('off', 'on')
    def turn_on(self):
        pass

    @transition('on', 'off')
    def turn_off(self):
        pass


class Switch(object):
    """
    Test fixture which implements a basic on/off switch state machine.
    """

    def __init__(self, state_machine):
        self.state_machine = state_machine

    def is_initial_state(self):
        return self.state_machine.state == self.state_machine.initial_state

    def is_on(self):
        return self.state_machine.state == 'on'

    def is_off(self):
        return self.state_machine.state == 'off'

    @property
    def state(self):
        return self.state_machine.state

    def turn_on(self):
        return self.state_machine.turn_on()

    def turn_off(self):
        return self.state_machine.turn_off()

    @guard('on')
    def call_when_on(self):
        return True

    @guard('off')
    def call_when_off(self):
        return True


def test_transitions_wrapper(switch_state_machine):
    """
    Wrapping methods in @transitions descriptors should expose a `transition`
    object on the method which contains execution data. Also, these decorated
    functions should look and act as the original function.
    """
    assert hasattr(switch_state_machine.turn_off, 'transition')

    t = switch_state_machine.turn_off.transition
    assert t.action.__name__ == switch_state_machine.turn_off.__name__
    assert t.action.__module__ == switch_state_machine.turn_off.__module__
    assert t.action.__doc__ == switch_state_machine.turn_off.__doc__


def test_transition_current_state_set(switch_state_machine):
    """
    Test that `current_state` and `next_state` values are properly
    stored when using @transition descriptors.
    """
    assert switch_state_machine.turn_off.transition.current_state == 'on'
    assert switch_state_machine.turn_off.transition.next_state == 'off'

    assert switch_state_machine.turn_on.transition.current_state == 'off'
    assert switch_state_machine.turn_on.transition.next_state == 'on'


def test_transitions_change_state(switch):
    """
    Calling methods wrapped in @transition descriptors should correctly
    change the `state` attribute of the `StateMachine` and it should be equal
    to that of that transitions `next_state` attribute.
    """
    # Flip on.
    switch.turn_on()
    assert switch.is_on()
    assert switch.state == switch.state_machine.turn_on.transition.next_state

    # Flip off.
    switch.turn_off()
    assert switch.is_off()
    assert switch.state == switch.state_machine.turn_off.transition.next_state


def test_invalid_transition_raises(switch):
    """
    Attempting to perform an invalid transition should raise a
    :class: `~scatter.state.InvalidTransition` exception.
    """
    with pytest.raises(InvalidTransition):
        switch.turn_off()
        assert switch.is_off()


def test_valid_state_guard_called(switch):
    """
    Calling methods wrapped in @guard descriptors should be called
    if the state machine is in that guarded state.
    """
    assert switch.is_off()
    assert switch.call_when_off()

    switch.turn_on()
    assert switch.is_on()
    assert switch.call_when_on()


def test_invalid_state_guard_raises(switch):
    """
    Calling methods wrapped in @guard descriptors should raise a
    :class: `~scatter.state.InvalidTransition` exception when called when in an invalid state.
    """
    with pytest.raises(InvalidTransition):
        switch.call_when_on()