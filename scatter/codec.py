"""
    scatter.codec
    ~~~~~~~~~~~~~

    Implements objects to support multiple wire data formats.
"""


import abc
import json

try:
    import cPickle as pickle
except ImportError:
    import pickle


class CodecError(Exception):
    """

    """
    pass


class DecodingError(CodecError):
    """

    """
    pass


class EncodingError(CodecError):
    """

    """
    pass


class Codec(object):
    """

    """

    __metaclass__ = abc.ABCMeta

    def encode(self, obj, **kwargs):
        raise NotImplementedError('Abstract method must be implemented in derived class.')

    def decode(self, msg, **kwargs):
        raise NotImplementedError('Abstract method must be implemented in derived class.')


class JsonCodec(Codec):
    """

    """
    def encode(self, obj, **kwargs):
        return json.dumps(obj, **kwargs)

    def decode(self, msg, **kwargs):
        return json.loads(msg, **kwargs)


class PickleCodec(Codec):
    """

    """
    def encode(self, obj, **kwargs):
        return pickle.dumps(obj, **kwargs)

    def decode(self, msg, **kwargs):
        return pickle.loads(msg)