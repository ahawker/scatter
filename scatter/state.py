"""
    scatter.state
    ~~~~~~~~~~~~~

    Control service functionality when it changes state.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('InvalidTransition', 'transition', 'guard', 'StateMachine')


import collections
import contextlib
import functools
import itertools

from scatter.descriptors import cached
from scatter.utils import iterable


NO_OP = lambda *args, **kwargs: True


class InvalidTransition(Exception):
    """
    """


class Transition(object):
    """
    Descriptor which allows users to decorate multiple functions to compose a state transition. Transitions
    are composed of up to four separate functions:

    condition -> Callable to return a bool which denotes if the transition should be executed.
    enter -> Callable to be executed before the action.
    action -> The meat of the transition.
    exit -> Callable to be executed after the action.

    Example:

    class LightSwitch(object):
        state = 'off'

        @transition('off', 'on')
        def on(self):
            print 'Let there be light!'

        @on.enter
        def beg(self):
            print 'Please be kind; I am afraid of the dark.'

        @transition('on', 'off')
        def off(self):
            print 'The darkness engulfs you.'

        @off.exit:
        def at_ease(self):
            print 'Thank you! I hate the dark!'
    """

    def __init__(self, current_state, next_state, action=None, condition=None, enter=None, exit=None):
        self.current_state = current_state
        self.next_state = next_state

        self.action = action
        self.condition = condition or NO_OP
        self.on_enter = enter or NO_OP
        self.on_exit = exit or NO_OP

    def __call__(self, func, *args, **kwargs):
        if func is not None:
            functools.update_wrapper(self, func)
        self.action = func
        return self

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.wrapper(instance)

    @cached
    def event(self):
        """
        Asynchronous event which allows other execution contexts to wait for this
        specific transition to complete.

        ..note: Usage
        The main use case for such asynchronous events is that of a the main execution
        thread waiting for the running service to stop.
        """
#        from scatter.async import Event
        from threading import Event
        return Event()

    def guard(self, func):
        """
        Wrapped function which is called to determine if the state machine should
        perform this transition.

        :param func: Callable which returns a boolean indicating whether or not we should perform transition.
        """
        self.condition = func
        return self

    def enter(self, func):
        """
        Wrapped function which is called just before a transition is performed.

        :param func: Callable which is called before the transition action.
        """
        self.on_enter = func
        return self

    def exit(self, func):
        """
        Wrapped function which is called just after a transition is performed.

        :param func: Callable which is called after the transition action.
        """
        self.on_exit = func
        return self

    def wait(self, timeout=None):
        """
        Wait for this transition to complete.

        :param timeout: (Optional) number of seconds to wait for transition to complete. Defaults to `None`.
        """
        self.event.wait(timeout)

    @contextlib.contextmanager
    def transition(self, *args, **kwargs):
        """
        Context manager which executes a transition from within the scope of a `with` statement.

        :param args: (Optional) Arguments to be passed to enter/exit actions.
        :param kwargs: (Optional) Keyword arguments passed to enter/exit actions.
        """
        self.on_enter(*args, **kwargs)
        yield self
        self.on_exit(*args, **kwargs)
        self.event.set()

    def wrapper(self, state_machine):
        """
        Returns a function which executes the entire flow of a transition.

        :param state_machine: Instance of the object whose functions are decorated with @transition.
        """
        def decorator(*args, **kwargs):
            """
            Decorator which encapsulates execution of a single transition.
            """
            state = state_machine.state

            # Ignore transitions which cannot execute within the current state.
            if not state in iterable(self.current_state):
                raise InvalidTransition('Cannot transition to {0} from {1}'.format(state, self.current_state))

            # Ignore transitions whose guard conditions fail to return True.
            if not bool(self.condition(state_machine, *args, **kwargs)):
                return state

            # Perform a state transition.
            with self.transition(state_machine, *args, **kwargs) as transition:
                transition.action(state_machine, *args, **kwargs)

                # Move to next state and record a log of all transitions so we can
                # playback/rewind the service lifecycle..
                state = state_machine.state = self.next_state
                state_machine.log.append(state)
                return state

        # Attach descriptor to wrapped transition func to allow for state "lookup" so we can playback/rewind
        # an entire object transition lifecycle.
        functools.update_wrapper(decorator, self.action)
        decorator.transition = self
        return decorator


transition = Transition


class StateGuardDescriptor(object):
    """
    Descriptor which allows objects that expose a :attr: `state_machine` to guard
    their functions to only be called when in a specified state.
    """

    def __init__(self, state, func=None):
        self.state = state
        self.func = func

    def __call__(self, func):
        """
        """
        if func is not None:
            functools.update_wrapper(self, func)
        self.func = func
        return self

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.wrapper(instance)

    def wrapper(self, instance):
        """
        Return a function which wraps the decorated function and calls it if the
        instance this descriptor is attached to is in the expected state.

        :param instance: Object instance which exposes a state machine.
        """
        def decorator(*args, **kwargs):
            """
            Decorator which validates the current state vs expected and calls
            the function when valid.
            """
            # If the instance isn't a state machine, raise an error.
            state_machine = getattr(instance, 'state_machine', None)
            if state_machine is None:
                raise RuntimeError('@guard descriptor must be used on classes which implement a state machine')

            state = state_machine.state
            # Raise error if current state isn't one of our valid states.
            if not state in iterable(self.state):
                raise InvalidTransition('{0} cannot be called in state {1}'.format(self.func.__name__, state))

            return self.func(instance, *args, **kwargs)

        return decorator


guard = StateGuardDescriptor


class StateMachine(object):
    """
    Basic StateMachine which supports lookup, playback and rewind of transitions
    generated by the :class: `~scatter.state.Transition` descriptor.
    """

    state = initial_state = None

    def __init__(self, initial_state):
        self.state = self.initial_state = initial_state
        self.log = StateMachineLog(initial_state)

    @cached
    def transitions(self):
        """
        Lookup table of all transitions within this state machine.
        """
        t = collections.defaultdict(dict)

        # Find all state machine functions wrapped with a @transition descriptor.
        descriptors = (t for t in (getattr(self, f) for f in dir(self) if f != 'transitions') if hasattr(t, 'transition'))
        for descriptor in descriptors:
            for state in iterable(descriptor.transition.current_state):
                t[state][descriptor.transition.next_state] = descriptor

        return dict(t)

    def to_state(self, state, *args, **kwargs):
        """
        Performs a forced transition to the given state.

        :param state: Next state to transition to.
        :param args: (Optional) Arguments to be consumed by transition.
        :param kwargs: (Optional) Keyword arguments to be consumed by the transition.
        """
        transition = self.transitions.get(self.state).get(state)
        if transition is None:
            return self.state
        state = self.state = transition(self, *args, **kwargs)
        return state

    def playback(self):
        """
        Generator which yields back historical transitions performed by this state machine,
        starting with its initial state.
        """
        return (s for s in self.log)

    def rewind(self):
        """
        Generator which yields back historical transitions performed by this state machine,
        starting with its current state.
        """
        return (s for s in reversed(self.log))

    def fast_forward(self, state_machine, *args, **kwargs):
        """
        Fast-forward this state machine to the current state of the given state machine.

        :param state_machine: State machine to replay to reach an identical state.
        """
        # Replay slice of state log for all transitions beyond our current state.
        for state in state_machine.log.replay(self.state):
            self.to_state(state, *args, **kwargs)
        return self.state


class StateMachineLog(object):
    """
    Log of all state transitions made by a :class: `~scatter.state.StateMachine`.
    """

    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.log = collections.deque((initial_state,))

    def __contains__(self, item):
        return item in self.log

    def __iter__(self):
        return iter(self.log)

    def __len__(self):
        return len(self.log)

    def append(self, state):
        self.log.append(state)

    def popleft(self):
        return self.log.popleft()

    def popright(self):
        return self.log.pop()

    def replay(self, start_state=None):
        """
        Replay state machine transitions up until its current state.

        :param start_state: (Optional) state to start the playback from. Defaults to initial_state.
        """
        # State at which to start the replay of the log (exclusive).
        if start_state is None:
            start_state = self.initial_state

        # Drop entries until we reach our start state and slice it off.
        log = itertools.dropwhile(lambda s: s != start_state, self.log)
        return itertools.islice(log, 1, None)
