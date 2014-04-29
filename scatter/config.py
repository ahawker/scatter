"""
    scatter.config
    ~~~~~~~~~~~~~~

    Store, load, and manage service configuration data.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('Config', 'ConfigAttribute')


from scatter.descriptors import MetaDescriptor
from scatter.structures import ScatterDict


class ConfigException(Exception):
    """

    """


class ConfigAttribute(MetaDescriptor):
    """
    Descriptor to mark and forward class attributes to use the service configuration.

    ..example::
        class MyService(Service):
            full_name = ConfigAttribute('Homer Simpson')

        s = MyService()
        s.full_name
        >> 'Homer Simpson'
        s.full_name = 'Milhouse Van Houten'
        s.full_name
        >> 'Milhouse Van Houten

    """

    def __init__(self, default=None, abstract=False):
        self.default = default
        self.abstract = abstract

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        value = instance.config.setdefault(self.__name__, self.default)
        if self.abstract is True and value is self.default:
            raise ConfigException("Abstract config attribute '{0}' must be set".format(self.__name__))

        return value

    def __set__(self, instance, value):
        instance.config[self.__name__] = value

    def __delete__(self, instance):
        del instance.config[self.__name__]


class Config(ScatterDict):
    """
    Collection of service configuration values.
    """
    def filter(self, key):
        return key.isupper()

    def transform(self, key):
        return key.upper()
