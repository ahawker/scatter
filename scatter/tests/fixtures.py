"""
    scatter.tests.fixtures
    ~~~~~~~~~~~~~~~~~~~~~~
"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'
__all__ = ('ScatterLogCapture',)


import testfixtures


class ScatterLogCapture(testfixtures.LogCapture):
    """

    """

    def __init__(self, service, *args, **kwargs):
        super(ScatterLogCapture, self).__init__(*args, **kwargs)
        self.service = service

    def assert_info(self, msg):
        self.assert_message('INFO', msg)

    def assert_debug(self, msg):
        self.assert_message('DEBUG', msg)

    def assert_warning(self, msg):
        self.assert_message('WARNING', msg)

    def assert_error(self, msg):
        self.assert_message('ERROR', msg)

    def assert_exception(self, msg):
        self.assert_message('EXCEPTION', msg)

    def assert_message(self, category, message):
        self.check(('root', category, message))