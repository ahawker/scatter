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
import time
import weakref

from scatter.descriptors import cached
from scatter.utils import iterable
from scatter.uid import urn


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

    def __init__(self, current_state=None, next_state=None, action=None, condition=None, enter=None, exit=None):
        self.current_state = current_state
        self.next_state = next_state

        self.action = action
        self.condition = condition or NO_OP
        self.on_enter = enter or NO_OP
        self.on_exit = exit or NO_OP

    def __call__(self, func, *args, **kwargs):
        if func is not None:
            functools.update_wrapper(self, func)
        return self.update(action=func)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.wrapper(instance)

    def update(self, action=None, condition=None, enter=None, exit=None):
        """
        Create a new `Transition` instance composed of the updated transition functions.
        """
        return type(self)(self.current_state,
                          self.next_state,
                          action=action or self.action,
                          condition=condition or self.condition,
                          enter=enter or self.on_enter,
                          exit=exit or self.on_exit)

    def guard(self, func):
        """
        Wrapped function which is called to determine if the state machine should
        perform this transition.

        :param func: Callable which returns a boolean indicating whether or not we should perform transition.
        """
        return self.update(condition=func)

    def enter(self, func):
        """
        Wrapped function which is called just before a transition is performed.

        :param func: Callable which is called before the transition action.
        """
        return self.update(enter=func)

    def exit(self, func):
        """
        Wrapped function which is called just after a transition is performed.

        :param func: Callable which is called after the transition action.
        """
        return self.update(exit=func)

    @contextlib.contextmanager
    def transition(self, state_machine, *args, **kwargs):
        """
        Context manager which executes a transition from within the scope of a `with` statement. A
        transition will run within the content manager of the given state machine and explicitly
        call the transitions `on_enter` and `on_exit` event functions.

        :param args: (Optional) Arguments to be passed to enter/exit actions.
        :param kwargs: (Optional) Keyword arguments passed to enter/exit actions.
        """
        with state_machine:
            try:
                self.on_enter(state_machine, *args, **kwargs)
                yield self
            except:
                raise
            finally:
                self.on_exit(state_machine, *args, **kwargs)

    def wrapper(self, state_machine):
        """
        Returns a function which executes the entire flow of a transition.

        :param state_machine: Instance of the object whose functions are decorated with @transition.
        """
        def wait(*args, **kwargs):
            """
            Helper function which exposes state transition events on
            transition descriptor objects.
            """
            return state_machine.wait_for_state(self.next_state, *args, **kwargs)

        def decorator(*args, **kwargs):
            """
            Decorator which encapsulates execution of a single transition.
            """
            state = state_machine.state

            # Ignore transitions which cannot execute within the current state.
            if not state in iterable(self.current_state):
                return state

            # Ignore transitions whose guard conditions fail to return True.
            if not bool(self.condition(state_machine, *args, **kwargs)):
                return state

            # Perform a state transition.
            with self.transition(state_machine, *args, **kwargs) as t:
                t.action(state_machine, *args, **kwargs)
                state = state_machine.state = self.next_state
                return state

        # Attach descriptor and helper functions to the decorator for easy use.
        functools.update_wrapper(decorator, self.action)
        decorator.transition = self
        decorator.wait = wait

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
        return self.update(func)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return self.wrapper(instance)

    def update(self, func=None):
        """
        Create a new `StateGuardDescriptor` instance composed of the updated function.
        """
        return type(self)(self.state, func or self.func)

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

    #:
    #:
    state = initial_state = None

    def __init__(self, initial_state, event_cls):
        self.state = self.initial_state = initial_state
        self.event = event_cls()

    def __enter__(self):
        self.event.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_info = (exc_type, exc_val, exc_tb)
        if not all(exc_info):
            self.event.notify_all()
        self.event.release()

    def wait_for_state(self, state, timeout=None):
        """
        Block the caller for the given number of seconds waiting for the state machine
        to enter the given state.
        """
        end = None
        remaining = timeout

        with self.event:
            while self.state != state:
                if timeout is not None:
                    if end is None:
                        end = time.time() + timeout
                    else:
                        remaining = end - time.time()
                        if remaining <= 0:
                            return False
                self.event.wait(remaining)
        return True
