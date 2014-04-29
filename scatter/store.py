"""
    scatter.store
    ~~~~~~~~~~~~~

"""


import abc


class Store(object):
    """

    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __len__(self):
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def pop(self, key, default=None):
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def get(self, key, default=None):
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def put(self, key, value):
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    @abc.abstractmethod
    def delete(self, key):
        raise NotImplementedError('Abstract method must be implemented in derived class.')


class DictStore(Store):
    """

    """

    def __init__(self, *args, **kwargs):
        self.data = dict(*args, **kwargs)

    def __len__(self):
        return len(self.data)

    def pop(self, key, default=None):
        return self.data.pop(key, default)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def put(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]
