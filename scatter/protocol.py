"""
    scatter.protocol
    ~~~~~~~~~~~~~~~~

    Implements objects which define the scatter wire protocol.

"""
__all__ = []

import uid

from scatter.codec import Codec, CodecError, DecodingError, EncodingError
from scatter.config import ConfigAttribute
from scatter.descriptors import cached
from scatter.service import Service


class Message(object):
    """

    """
    required_fields = 'sender_id msg_id, topic func args kwargs'.split()

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def pack(cls, **obj):
        """

        """
        obj.setdefault('msg_id', uid())
        obj.setdefault('topic', '')
        obj.setdefault('args', ())
        obj.setdefault('kwargs', {})

        msg = dict((k, v) for (k, v) in obj if k in cls.required_fields)
        if len(msg) < len(cls.required_fields):
            raise EncodingError('Packed message is missing required fields!')
        return msg

    @classmethod
    def unpack(cls, **msg):
        """

        """
        msg = dict((k, v) for (k, v) in msg if k in cls.required_fields)
        if len(msg) < len(cls.required_fields):
            raise DecodingError('Unpacked message is missing required fields!')
        return Message(**msg)

    def __getattr__(self, item):
        return self.__dict__.get(item, None)

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        return self

    def __delattr__(self, item):
        del self.__dict__[item]
        return self


class Protocol(Service):
    """

    """

    #:
    #:
    message_class = ConfigAttribute()

    #:
    #:
    use_compression = ConfigAttribute()

    #:
    #:
    compression_class = ConfigAttribute()

    @cached
    def codec(self):
        return self.services.by_type(self.codec_class).first()

    def encode(self, obj, codec=None):
        """
        """
        codec = codec or self.codec
        msg = self.message_class.pack(**obj)
        return codec.encode(msg)

    def decode(self, msg, codec=None):
        """
        """
        codec = codec or self.codec
        msg = codec.decode(msg)
        return self.message_class.unpack(**msg)

    def on_initializing(self, *args, **kwargs):
        """
        """
        self.config.setdefault('MESSAGE_CLASS', Message)
        self.config.setdefault('USE_COMPRESSION', False)
        self.config.setdefault('COMPRESSION_CLASS', None) #TODO
        self.config.setdefault('CODEC_CLASS', Codec)

    def on_starting(self, *args, **kwargs):
        pass

    def on_stopping(self, *args, **kwargs):
        pass


class MessageHandler(Service):
    """

    """

    #:
    #:
    protocol_class = ConfigAttribute()

    @cached
    def protocol(self):
        return self.services.by_type(self.protocol_class).first()

    def on_recv_callback(self, stream, msg):
        """
        """
        try:
            msg = self.protocol.decode(msg, stream.codec)
        except CodecError as e:
            self.log.error('Unable to decode message. {0}'.format(e.message))
        else:
            try:
                self.parent.on_msg_recv(stream, msg)
            except Exception as e:
                self.log.error('Exception raised in on_msg_recv callback. {0}'.format(e.message))

    def on_send_callback(self, stream, msg):
        """
        """
        try:
            self.parent.on_msg_send(stream, msg)
        except Exception as e:
            self.log.error('Exception raised in on_msg_send callback. {0}'.format(e.message))

    def on_initializing(self, *args, **kwargs):
        """
        """
        self.config.setdefault('PROTOCOL_CLASS', Protocol)



# class Protocol(object):
#     """
#     Scatter protocol.
#
#     Frame 0: {header}
#     Frame 1: {payload}
#
#     Header::
#         uri
#         msg_id
#         topic
#
#     Payload::
#         method
#         args
#         kwargs
#
#     """
#     def __init__(self, codec=None, compress=False):
#         #self.codec = codecs.Codec(codec or 'json') #TODO
#         self.codec = codecs.JSON()
#         self.compress = int(compress)
#
#     def encode(self, **kwargs):
#         msg = Message.pack(**kwargs)
#         return self.codec.encode(msg)
#
#     def decode(self, msg):
#         msg = self.codec.decode(msg)
#         return Message.unpack(msg)

    # def encode_msg(self, uri, method, args, kwargs, msg_id=None, topic=None):
    #     msg_id = msg_id or generate_msg_id()
    #     header = dict(uri=uri, msg_id=msg_id, topic=topic)
    #     payload = dict(method=method, args=args, kwargs=kwargs)
    #     msg = Message(**dict(header, **payload))
    #     return self.codec.encode(msg.pack())
    #
    # def decode_msg(self, msg):
    #     msg = self.codec.decode(msg)
    #     return Message(**msg)
    #
    # def encode_result(self): #hrm
    #     pass
    #
    # def decode_result(self): #hrm
    #     pass


#
# class Message(object):
#     pass
#
#
#
# #I want attr access!!!
#
# #msg.uri = ...
# #msg.
#
# #action => call or cast => (sync, async respectively)
# #method => __exec__, __eval__, __getattr__, __setattr__, __proxy__ ???? (__call__ should be encapulated under exec)
#
#
# class Message(object):
#     required_attributes = []
#
#     def __init__(self, **kwargs):
#         if not kwargs or not all(k in kwargs for k in self.required_attributes):
#             raise ValueError('Message is missing required fields.')
#         self.__dict__.update(kwargs)
#
#
# class Request(Message):
#     def __init__(self, action, method):
#         pass
#
#
# class Response(Message):
#     pass
#
#
# class Message(object):
#     required_attributes = 'uri payload'.split()
#
#     def __init__(self, **kwargs):
#         if not kwargs or not all(k in kwargs for k in self.required_attributes):
#             raise ValueError('Message header is missing required fields.')
#         kwargs.setdefault('msgid', generate_msg_id())
#         kwargs.setdefault('topic', '')
#         self.__dict__['_data'] = kwargs
#
#     @classmethod
#     def pack(cls, **kwargs):
#         if not kwargs or not all(k in kwargs for k in cls.required_attributes):
#             raise ValueError('Message is missing required fields.')
#
#         kwargs.setdefault('msgid', generate_msg_id())
#         kwargs.setdefault('topic', '')
#         header = dict(uri=kwargs['uri'], msgid=kwargs['msgid'], topic=kwargs['topic'])
#         return dict(header=header, payload=kwargs['payload'])
#
#     @classmethod
#     def unpack(cls, msg):
#         header, payload = msg
#
#
#     def __iter__(self):
#         return iter(self._data)
#
#     def __getattr__(self, item):
#         return self._data.get(item)
#
#     def __setattr__(self, key, value):
#         pass #TODO
#
#     def __delattr__(self, item):
#         pass #TODO
#
#
# if __name__ == '__main__':
#     d = {
#         'name': 'andrew',
#         'age': 25
#     }
#     m = Message(**d)
#     print m
#     print dir(m)