"""
    scatter.exceptions
    ~~~~~~~~~~~~~~~~~~

    Scatter specific exceptions.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('ScatterExit', 'ScatterCancel', 'ScatterTimeout', 'ServiceDependencyError')


class ScatterException(Exception):
    """

    """


class ScatterExit(ScatterException):
    """

    """


class ScatterCancel(ScatterException):
    """

    """


class ScatterTimeout(ScatterException):
    """

    """


class ServiceDependencyError(ScatterException):
    """

    """