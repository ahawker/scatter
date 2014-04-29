"""
    scatter.stream
    ~~~~~~~~~~~~~~

"""


import abc

from scatter.socket import Socket


class Stream(Socket):
    """

    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, stream):
        super(Stream, self).__init__(stream)
        self._stream = stream

    @abc.abstractmethod
    def on_send(self, func):
        """

        :return:
        """
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def on_recv(self, func):
        """

        :return:
        """
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def on_close(self, func):
        raise NotImplementedError('Abstract method must be implemented in derived class.')
