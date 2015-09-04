"""
    scatter.meta
    ~~~~~~~~~~~~

    Useful introspection methods into the python type system.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('resolve_class', 'resolve_type', 'resolve_type_meta',
           'get_public_attrs', 'get_instance_descriptors', 'is_abstract')


import inspect


NO_OP = lambda *args, **kwargs: True


def is_abstract(cls):
    """
    Returns `True` if the given class object is marked with the `__abstract__`
    attribute.
    """
    return cls.__dict__.get('__abstract__', False) is True


def resolve_callable(func):
    """

    """
    bound = hasattr(func, 'im_self')
    if bound:
        return repr(func)

    return func.__name__


def resolve_class(obj):
    """
    Return class name for the given object.
    """
    if inspect.isclass(obj):
        return obj.__name__
    return getattr(obj, '__class__', obj).__name__


def resolve_module(obj):
    """
    Return module name of for the given object.
    """
    return getattr(obj, '__module__', '__main__')


def resolve_type(obj):
    """
    Return the fully qualified type string for the given object. The fully-qualified type
    is a period separated string of module name and class name.

    Example: my.package.module.class
    """
    cls = resolve_class(obj)
    module = resolve_module(obj)
    return '{0}.{1}'.format(module, cls)


def resolve_type_meta(name, attrs):
    """
    Return the fully qualified type string for the class being created by
    a meta class.
    """
    module = attrs.get('__module__', '__main__')
    return '{0}.{1}'.format(module, name)


def get_filtered_object_attrs(obj, predicate=NO_OP):
    """
    Return generator which yields name/value pairs of all attributes of the given object
    which fulfill the given predicate.

    :param obj: Object to find attributes for.
    :param predicate: (Optional) function which should return True for attribute names it wishes to handle.
    """
    return ((name, getattr(obj, name, None)) for name in dir(obj) if predicate(name))


def get_public_attrs_gen(obj):
    """
    Return generator which yields name/value pairs of all `public` attributes of the given object.
    Attributes are classified as `public` if their name doesn't start with an underscore.

    :param obj: Object to find public attributes for.
    """
    def _is_public(name):
        return not name.startswith('_')

    return get_filtered_object_attrs(obj, _is_public)


def get_public_attrs(obj):
    """
    Return dict of all `public` attributes of the given object. Attributes are
    classified as `public` if their name doesn't start with an underscore.

    :param obj: Object to find public attributes for.
    """
    return dict(get_public_attrs_gen(obj))


def get_typed_public_attrs_gen(obj, cls):
    """
    Return generator which yields name/value pairs of all attributes of the given object
    which are of the given class type.

    :param obj: Object to find typed attributes for..
    :param cls: Class of attributes to filter by.
    """
    return ((name, value) for name, value in get_public_attrs_gen(obj) if isinstance(value, cls))


def get_typed_public_attrs(obj, cls):
    """
    Return dict of all attributes of the given object which are of the given class type.

    :param obj: Object to find typed attributes for.
    :param cls: Class of attributes to filter by.
    """
    return dict(get_typed_public_attrs_gen(obj, cls))


def get_instance_descriptors_gen(obj, descriptor):
    """
    Return generator which yields pairs of instance attributes and their values
    which are defined as descriptors of the given type on its class.
    """
    for name, value in get_typed_public_attrs_gen(obj.__class__, descriptor):
        yield name, getattr(obj, name, None)


def get_instance_descriptors(obj, descriptor):
    """
    Return a dict containing pairs of instance attributes and their values
    which are defined as descriptors of the given type on its class.
    """
    return dict(get_instance_descriptors_gen(obj, descriptor))
