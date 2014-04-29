"""
    scatter.socket
    ~~~~~~~~~~~~~~

"""

import abc


class Socket(object):
    """

    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, socket):
        if socket is None:
            raise ValueError('socket cannot be none')
        self._socket = socket

    @abc.abstractproperty
    def socket_type(self):
        """

        :return:
        """
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def connect(self, address):
        """

        :return:
        """
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def bind(self, address):
        """

        :return:
        """
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def send(self, msg):
        """

        :return:
        """
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def recv(self):
        """

        :return:
        """
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def close(self):
        """

        :return:
        """
        raise NotImplementedError('Abstract method must be implemented in derived class.')
