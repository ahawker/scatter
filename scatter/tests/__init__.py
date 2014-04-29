"""
    scatter.tests
    ~~~~~~~~~~~~~

    ...
"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'

import unittest

from scatter.tests import core
from scatter.tests.core import *
from scatter.tests import fixtures
from scatter.tests.fixtures import *

__all__ = ('main', 'suite', 'ScatterTestLoader') + core.__all__ + fixtures.__all__


def suite():
    """

    """
    import os

    test_suite = unittest.TestSuite()
    for root, dirs, files in os.walk(os.path.dirname(__file__)):
        if '__init__.py' in files:
            tests = unittest.defaultTestLoader.discover(root, 'test_*.py')
            test_suite.addTest(tests)
    return test_suite


class ScatterTestLoader(unittest.TestLoader):
    """

    """

    @staticmethod
    def _tests_in_suite(name, suite):
        return suite

    def loadTestsFromName(self, name, module=None):
        """

        :param name:
        :param module:
        :return:
        """
        def _generate_tests_in_suite(name, suite):
            """

            :param suite:
            :return:
            """
            for testcase, testname in (t for t in self._tests_in_suite(name, suite)):
                if testname == name or name in testname:
                    yield testcase

        #Top level (full) test suite requested
        full_suite = suite()
        if name == 'suite':
            return full_suite

        #Find all tests for the given name
        tests = [t for t in _generate_tests_in_suite(name, full_suite)]
        if not tests or len(tests) == 0:
            raise RuntimeError('No tests found for name {0}'.format(name))

        return unittest.TestSuite(tests)


def main():
    """

    :return:
    """
    unittest.main(testLoader=ScatterTestLoader(), defaultTest='suite')


if __name__ == '__main__':
    main()