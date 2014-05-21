"""
    scatter.testing
    ~~~~~~~~~~~~~~~

    Implements common functionality to be used for testing the scatter package
    and its extensions.

    This module should not be used in production environments and outside of
    a test package.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('process', 'service')


import pytest
import unittest

from scatter.process import Process
from scatter.service import Service, ServiceState


class ScatterTestCase(unittest.TestCase):
    """
    Base class for all Scatter test cases.
    """

    @classmethod
    def setUpClass(cls):
        cls.setup_class()

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.teardown_class()

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        pass

    def setUp(self):
        self.setup()

    def teardown(self):
        pass

    def tearDown(self):
        self.teardown()

    def assert_raises(self, exc_type, callable_obj=None, *args, **kwargs):
        return self.assertRaises(exc_type, callable_obj, *args, **kwargs)

    def assert_true(self, expr, msg=None):
        return self.assertTrue(expr, msg)

    def assert_false(self, expr, msg=None):
        return self.assertFalse(expr, msg)

    def assert_in(self, member, container, msg=None):
        return self.assertIn(member, container, msg)

    def assert_not_in(self, member, container, msg=None):
        return self.assertNotIn(member, container, msg)

    def assert_is_none(self, obj, msg=None):
        return self.assertIsNone(obj, msg)

    def assert_is_not_none(self, obj, msg=None):
        return self.assertIsNotNone(obj, msg)

    def assert_greater(self, a, b, msg=None):
        return self.assertGreater(a, b, msg)

    def assert_greater_equal(self, a, b, msg=None):
        return self.assertGreaterEqual(a, b, msg)

    def assert_less(self, a, b, msg=None):
        return self.assertLess(a, b, msg)

    def assert_less_equal(self, a, b, msg=None):
        return self.assertLessEqual(a, b, msg)

    def assert_almost_equal(self, first, second, places=None, msg=None, delta=None):
        return self.assertAlmostEqual(first, second, places, msg, delta)

    def assert_equal(self, first, second, msg=None):
        return self.assertEqual(first, second, msg)

    def assert_not_equal(self, first, second, msg=None):
        return self.assertNotEqual(first, second, msg)

    def assert_not_almost_equal(self, first, second, places=None, msg=None, delta=None):
        return self.assertNotAlmostEqual(first, second, places, msg, delta)

    def assert_is(self, expr1, expr2, msg=None):
        return self.assertIs(expr1, expr2, msg)

    def assert_is_not(self, expr1, expr2, msg=None):
        return self.assertIsNot(expr1, expr2, msg)

    def assert_is_instance(self, obj, cls, msg=None):
        return self.assertIsInstance(obj, cls, msg)

    def assert_is_not_instance(self, obj, cls, msg=None):
        return self.assertNotIsInstance(obj, cls, msg)

    def assert_items_equal(self, expected_seq, actual_seq, msg=None):
        return self.assertItemsEqual(expected_seq, actual_seq, msg)

    def assert_tuple_equal(self, tuple1, tuple2, msg=None):
        return self.assertTupleEqual(tuple1, tuple2, msg)

    def assert_list_equal(self, list1, list2, msg=None):
        return self.assertListEqual(list1, list2, msg)

    def assert_sequence_equal(self, seq1, seq2, msg=None, seq_type=None):
        return self.assertSequenceEqual(seq1, seq2, msg, seq_type)

    def assert_set_equal(self, set1, set2, msg=None):
        return self.assertSetEqual(set1, set2, msg)

    def assert_dict_equal(self, d1, d2, msg=None):
        return self.assertDictEqual(d1, d2, msg)

    def assert_dict_contains_subset(self, expected, actual, msg=None):
        return self.assertDictContainsSubset(expected, actual, msg)

    def assert_multi_line_equal(self, first, second, msg):
        return self.assertMultiLineEqual(first, second, msg)

    def assert_regex_matches(self, text, expected_regex, msg=None):
        return self.assertRegexpMatches(text, expected_regex, msg)

    def assert_not_regex_matches(self, text, unexpected_regex, msg=None):
        return self.assertNotRegexpMatches(text, unexpected_regex, msg)

    def assert_raises_regex(self, expected_exc, expected_regex, callable_obj=None, *args, **kwargs):
        return self.assertRaisesRegexp(expected_exc, expected_regex, callable_obj, *args, **kwargs)

    def assert_len_greater(self, iterable, n):
        self.assert_greater(len(iterable), n)

    def assert_len_greater_equal(self, iterable, n):
        self.assert_greater_equal(len(iterable), n)

    def assert_len_less(self, iterable, n):
        self.assert_less(len(iterable), n)

    def assert_is_not_empty(self, iterable):
        return any(True for _ in iterable)


# class ServiceUnitTestCase(ScatterTestCase):
#     """
#     Base TestCase for all :class: `~scatter.service.Service` tests.
#     """
#
#     #:
#     #:
#     service_class = Service
#
#     #:
#     #:
#     service = None
#
#     #:
#     #:
#     default_config = dict()
#
#     def setup(self):
#         self.service = self.configure_service(self.service_class)
#
#     def teardown(self):
#         self.service = None
#
#     @classmethod
#     def setup_class(cls):
#         cls.service = cls.service_class()
#         cls.service = cls.configure_service(cls.service_class())
#         #cls.service.st
#         #cls.service = cls.service_class(config=dict(test=True))
#         #cls.service.test = True
#         #cls.service.start()
#
#     # @classmethod
#     # def teardown_class(cls):
#     #     cls.service.stop()
#
#     def configure_service(self, service_cls, config):
#         """
#         """
#         service = service_cls


# class ServiceIntegrationTestCase(ScatterTestCase):
#     """
#
#     """
#
#     #:
#     #:
#     #process_class = Process
#
#     #:
#     #:
#     process = None
#
#     def setup(self):
#         super(ProcessContextTestCase, self).setup()
#         #se
#
#     def configure_process(self):
#         pass
#         #self.process =


def create_test_process(factory, config):
    """
    Create a test process fixture from the given factory and configuration values.
    """
    process = factory()
    process.init()
    process.config.from_object(config)
    process.testing = True
    return process


def create_test_service(factory, config, process=None):
    """
    Create a test service fixture from the given factory and configuration values, optionally
    attached to a process service.
    """
    service = factory()
    service.init(process=process)
    service.config.from_object(config)
    service.testing = True
    return service


@pytest.fixture(scope='module')
def process(request):
    """
    Process service fixture tied to every test module which imports it. Can be configured
    by the following module level values:

    'process_factory': Callable which returns a process object.
    'process_config': Configuration values to set on process object.

    :param request: Request object passed from py.test containing fixture/test context.
    """
    factory = getattr(request.module, 'process_factory', Process)
    config = getattr(request.module, 'process_config', None)
    state = getattr(request.module, 'process_state', ServiceState.Initialized)

    return create_test_process(factory, state, config)


@pytest.fixture(scope='module')
def service(request, process=None):
    """
    Service fixture tied to every test module which imports it. Can be configured
    by the following module level values:

    'service_factory': Callable which returns a service object.
    'service_config': Configuration values to set on the service object.

    :param request: Request object passed from py.test containing fixture/test context.
    :param process: Optional process fixture to attach this service to.
    """
    factory = getattr(request.module, 'service_factory', Service)
    config = getattr(request.module, 'service_config', None)
    state = getattr(request.module, 'service_state', ServiceState.Initialized)

    return create_test_service(factory, config, state, process)


@pytest.fixture(scope='function')
def process_scope(request, process):
    print 'scope'
    process.start()
    request.addfinalizer(process.stop)