"""
    scatter.context
    ~~~~~~~~~~~~~~~

    Implements objects used to keep maintain service context.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('ProcessContext',)


from scatter.globals import app_ctx_stack


class Context(object):
    """
    """
    pass


class ProcessContext(object):
    """
    """

    def __init__(self, process):
        self.process = process