"""
    scatter.service
    ~~~~~~~~~~~~~~~

    Implements services, the building block of scatter applications.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.

"""
__all__ = ('Service',)


import contextlib
import functools
import inspect
import itertools
import weakref

from scatter.config import Config, ConfigAttribute
from scatter.descriptors import MetaDescriptor, cached
from scatter.exceptions import ScatterException
from scatter.importer import import_from
from scatter.log import create_logger, DEFAULT_LOG_LEVEL
from scatter.meta import resolve_type, resolve_class, resolve_type_meta,get_public_attrs, get_instance_descriptors, is_abstract
from scatter.registry import global_registry
from scatter.state import transition, guard, StateMachine
from scatter.structures import ScatterDict, ScatterMapping, ImmutableDict, Enum
from scatter.uid import urn
from scatter.utils import iterable


ServiceState = Enum('ServiceState', 'New Initialized Running Stopped')

new = guard(ServiceState.New)
initialized = guard(ServiceState.Initialized)
running = guard(ServiceState.Running)
stopped = guard(ServiceState.Stopped)

#running = None
#initialized = None
#stopped = None
#new = None

class ServiceResolveError(ScatterException):
    """

    """


class ServiceAttribute(MetaDescriptor):
    """
    Descriptor to mark and forward class attributes to use the service attributes collection.
    """

    def __init__(self, default=None):
        self.default = default

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.attributes.setdefault(self.__name__, self.default)

    def __set__(self, instance, value):
        instance.attributes[self.__name__] = value

    def __delete__(self, instance):
        del instance.attributes[self.__name__]


class ServiceAttributeCollection(ScatterDict):
    """

    """
    pass


class DependencyAttribute(MetaDescriptor):
    """
    Descriptor to mark and forward class attributes to use the service collection.
    """

    def __init__(self, func=None, type=None, cls=None, config=None):
        """

        :param func: (Optional) Callable passed if this descriptor is used as a decorator.
        :param type: (Optional) Fully-qualified type string of service dependency.
        :param cls: (Optional) Class object of service dependency.
        :param config: (Optional) Key into service config which resolves to a fully-qualified type string.
        """
        if func is not None:
            functools.update_wrapper(self, func)
        self.func = func
        self.type = type
        self.cls = cls
        self.config = config

    def __get__(self, instance, owner=None):
        """

        :param instance:
        :param owner:
        :return:
        """
        if instance is None:
            return self

        # Return the child service is one was previous created.
        service = instance.services.get(self.__name__)
        if service is not None:
            return service

        # Resolve the given constraints to a fully qualified type string for class.
        dependency = self._resolve_dependency(instance)
        if dependency is None:
            raise ServiceResolveError('Unable to resolve a fully qualified type from given dependency constraints')

        # No service found for this name, attempt to load/store/return a new instance.
        loader = self.func or self.load
        service = instance.services[self.__name__] = loader(instance, dependency)
        return service

    def __set__(self, instance, value):
        """

        :param instance:
        :param value:
        :return:
        """
        instance.services[self.__name__] = value

    def __delete__(self, instance):
        """

        :param instance:
        :return:
        """
        del instance.services[self.__name__]

    def load(self, instance, dependency):
        """
        Load and store a new dependent service within the given service instance.

        :param instance: Instance of service which owns this dependency.
        :param dependency: Fully qualified type string or class.
        """
        # Check registry to see if class has already been loaded.
        registry = getattr(instance, 'registry', None)
        if registry is None:
            raise ServiceResolveError('No service registry for {0}'.format(instance))

        # If dependency was set via 'cls', it's an already loaded class instance. Otherwise
        # it will be a fully qualified type string. If it is already loaded, we assume that its
        # fully qualified type is stored in the registry. I'm not sure that is valid?
        if inspect.isclass(dependency):
            cls = dependency
        else:
            # Query registry for fully qualified type if its already loaded, otherwise import it.
            #
            # .. note:: Side-effects
            # import_from will search sys.modules and load it if not already imported.
            # All loaded services will have their ServiceMeta.__new__ automatically called.
            # This will load it into its service registry (defaults to: `scatter.registry.global_registry`)
            # so it can be easily found for all future calls. The side-effect is that importing can potentially
            # import other services into the registry as well and that services might define a custom registry
            # which we won't know until after it is imported.
            cls = registry.get(dependency) or import_from(dependency)
            if cls is None:
                raise ServiceResolveError('No service found for {0}'.format(dependency))

        # If the class is abstract, query registry for first concrete subclass.
        if cls.is_abstract():
            print 'ABS: {0} CONC: {1}'.format(cls, list(registry.get_concrete_types(cls)))
            cls = registry.get_concrete_type(cls)

        instance.log.info("Dependency '{0}' of type {1} loaded service {2}.".format(self.__name__,
                                                                                    dependency,
                                                                                    cls))

        # Create and attach newly created dependency to service which requires it.
        return instance.child(cls, name=self.__name__)

    def _resolve_dependency(self, instance):
        """
        Resolve given constraints to either a fully qualified type string or class.

        :param instance: Instance of service which owns this dependency.
        """
        # Look into service config for the value of this dependency.
        # Set our type or cls based on the config value, fail on anything else.
        if self.config:
            value = instance.config.get(self.config, None)
            if inspect.isclass(value):
                self.cls = value
            elif isinstance(value, basestring):
                self.type = value
            else:
                instance.error.warning('Invalid dependency config value {0} of type {1}.'.format(self.config,
                                                                                                 type(value)))
        return self.cls or self.type or None

    def _resolve(self, instance):
        pass


class ServiceMeta(type):
    """
    Service metaclass which processes service descriptors and registers all
    unique service implementation types into a registry.
    """

    def __new__(mcs, name, bases, attrs):
        """
        """
        # Tag all :class: `~scatter.descriptors.MetaDescriptor`attached
        # to this new service class.
        for k, v in attrs.iteritems():
            if isinstance(v, MetaDescriptor):
                v.__name__ = k

        # If not already registered, add this Service class type to the registry.
        registry = attrs.setdefault('registry', global_registry)
        fully_qualified_type = resolve_type_meta(name, attrs)
        if fully_qualified_type not in registry:
            cls = super(ServiceMeta, mcs).__new__(mcs, name, bases, attrs)
            registry.register(fully_qualified_type, cls)

        # Return our newly created Service class.
        return registry[fully_qualified_type]


class ServiceCollection(ScatterMapping):
    """
    Collection which contains all children services of a service.
    """

    def __init__(self, service, services=None):
        import collections
        #super(ServiceCollection, self).__init__(weakref.WeakValueDictionary) #should be weakvalue + ordered!! TODO
        super(ServiceCollection, self).__init__(collections.OrderedDict)
        self.service = service
        if services is not None:
            self.add(services)

    def add(self, services):
        for service in iterable(services):
            self[service.id] = service

    def remove(self, services):
        for service in iterable(services):
            if isinstance(service, Service):
                service = service.id
            del self[service]

    def first(self, default=None):
        return next(iter(self), default)

    def all(self):
        return self.values()

    def by_state(self, state):
        return ServiceCollection(self.service, self.slice(lambda k, v: v.state_machine.state == state))

    def by_type(self, service_type):
        return ServiceCollection(self.service, self.slice(lambda k, v: isinstance(v, service_type)))

    def by_name(self, service_name):
        return ServiceCollection(self.service, self.slice(lambda k, v: k == service_name.lower()))

    def by_fully_qualified_type(self, fully_qualified_type):
        return self.by_attr('fully_qualified_type', fully_qualified_type)

    def by_attr(self, attr, default=None):
        return ServiceCollection(self.service, self.slice(lambda k, v: getattr(v, attr, default) == attr))

    def by_func(self, predicate):
        return ServiceCollection(self.service, self.slice(predicate))

    def slice(self, predicate=None, start=None):
        return itertools.islice(self.filter(predicate), start)

    def filter(self, predicate=None):
        if predicate is None:
            predicate = lambda k, v: True
        return ((k, v) for (k, v) in self.iteritems() if predicate(k, v))


class ServiceStateMachine(StateMachine):
    """
    StateMachine which describes basic functionality of how a service should operate.

    ..States::
        `new`:: Service class created. :method: `scatter.service.Service.__new__` called.
        `initialized`:: Service instance created. :method: `scatter.service.Service.__init__` called.
        `running`:: Service running. :method: `scatter.service.Service.start` called.
        `stopped`:: Service stopped. :method: `scatter.service.Service.stop` called.

    ..Transitions::
        `init`:: new -> initialized
        `start`:: initialized -> running
        `stop`:: (initialized, running) -> stopped
        `reload`:: running -> running
    """
    import threading

    def __init__(self, service):
        import threading
        super(ServiceStateMachine, self).__init__(ServiceState.New, threading.Condition)
        self.service = service

    def is_new(self):
        return self.state == ServiceState.New

    def is_initialized(self):
        return self.state == ServiceState.Initialized

    def is_started(self):
        return self.state in (ServiceState.Running, ServiceState.Stopped)

    def is_running(self):
        return self.state == ServiceState.Running

    def is_stopped(self):
        return self.state == ServiceState.Stopped

    @transition(ServiceState.New, ServiceState.Initialized)
    def init(self, *args, **kwargs):
        self.service.initializing(*args, **kwargs)

    @init.enter
    def init(self, *args, **kwargs):
        self.service.log.info('Service initializing')
        self.service.on_initializing(*args, **kwargs)

    @init.exit
    def init(self, *args, **kwargs):
        self.service.on_initialized(*args, **kwargs)
        self.service.log.info('Service initialized')

    @transition((ServiceState.Initialized, ServiceState.Stopped), ServiceState.Running)
    def start(self, *args, **kwargs):
        self.service.starting(*args, **kwargs)

    @start.enter
    def start(self, *args, **kwargs):
        self.service.log.info('Service starting')
        self.service.on_starting(*args, **kwargs)

    @start.exit
    def start(self, *args, **kwargs):
        self.service.on_started(*args, **kwargs)
        self.service.log.info('Service started')

    @transition((ServiceState.Initialized, ServiceState.Running), ServiceState.Stopped)
    def stop(self, *args, **kwargs):
        self.service.stopping(*args, **kwargs)

    @stop.enter
    def stop(self, *args, **kwargs):
        self.service.log.info('Service stopping')
        self.service.on_stopping(*args, **kwargs)

    @stop.exit
    def stop(self, *args, **kwargs):
        self.service.on_stopped(*args, **kwargs)
        self.service.log.info('Service stopped')

    @transition(ServiceState.Running, ServiceState.Running)
    def reload(self, *args, **kwargs):
        self.service.reloading(*args, **kwargs)

    @reload.enter
    def reload(self, *args, **kwargs):
        self.service.log.info('Service reloading')
        self.service.on_reloading(*args, **kwargs)

    @reload.exit
    def reload(self, *args, **kwargs):
        self.service.on_reloaded(*args, **kwargs)
        self.service.log.info('Service reloaded')


class Service(object):
    """
    A service is a big ball of mud.
    """
    __metaclass__ = ServiceMeta

    #:
    #:
    process = None

    #:
    #:
    app = None

    #:
    #:
    parent = None

    #:
    #:
    log = None

    #: The class used for storing Service configuration data.
    #: Defaults to :class: `~scatter.config.Config`.
    config_class = Config

    #:
    #:
    config_file = ConfigAttribute()

    #: Toggle debug mode. Set this to `True` to enable service debug mode.
    #: Defaults to `False`.
    debug = ConfigAttribute(False)

    #: Toggle test mode. Set this to `True` to enable service test mode.
    #: Defaults to `False`.
    testing = ConfigAttribute(False)

    #: The class used for controlling the service. The service expects this class
    #: to provide the `init`, `start`, `stop` and `reload` functions at a minimum.
    #: Defaults to :class: `~scatter.service.ServiceStateMachine`.
    state_machine_class = ConfigAttribute('scatter.service.ServiceStateMachine')

    #: The class used to contain the attributes used to identify the service
    #: and describe its functionality.
    #: Defaults to :class: `~scatter.service.ServiceAttributeCollection`.
    attribute_collection_class = ConfigAttribute('scatter.service.ServiceAttributeCollection')

    #: The class used to contain the attached children services to this service.
    #: Defaults to :class: `~scatter.service.ServiceCollection`.
    service_collection_class = ConfigAttribute('scatter.service.ServiceCollection')

    #: Set the threshold for the service logger. Defaults to `INFO` (20).
    log_level = ConfigAttribute(DEFAULT_LOG_LEVEL)

    #:
    #:
    log_handler_class = ConfigAttribute()

    #: The logging format used for the service logger.
    log_format = ConfigAttribute(('%(asctime)s - %(processName)s - %(threadName)s - %(levelname)s - '
                                  '%(service_id)s - %(service_type)s - %(service_name)s - %(message)s'))

    #:
    #:
    log_formatter_class = ConfigAttribute()

    #: Set timeout for service shutdown time. Defaults to `5` seconds.
    stop_timeout = ConfigAttribute(5)

    #: Default configuration parameters.
    default_config = ImmutableDict({})

    #: Attribute which exposes a unique service identifier.
    id = ServiceAttribute()

    #: Attribute which exposes a human readable service name.
    name = ServiceAttribute()

    #: Attribute which exposes the service class.
    type = ServiceAttribute()

    #: Attribute which exposes the fully qualified service type.
    fully_qualified_type = ServiceAttribute()

    #: Default service attributes.
    default_attributes = ImmutableDict({})

    #: Lazy loaded dependency for Greenlet support.
    #: Provided by :class: '~scatter.async.eventlet.EventletService` or :class: `~scatter.async.gevent.GeventService`.
    # greenlets = AsyncDependencyAttribute(type='scatter.async.greenlet.GreenletService')
    #
    # #: Lazy loaded service dependency for Thread support.
    # #: Provided by :class: `~scatter.async.threading.ThreadingService`.
    # threads = AsyncDependencyAttribute(type='scatter.async.threading.ThreadingService')
    #
    # #: Lazy loaded service dependency for Multiprocess support.
    # #: Provided by :class: `~scatter.async.multiprocessing.ProcessService`.
    # processes = AsyncDependencyAttribute(type='scatter.async.multiprocessing.ProcessService')
    #
    # #: Lazy loaded service dependency for Subprocess support.
    # #: Provided by :class: `~scatter.async.subprocess.SubprocessService`.
    # subprocesses = AsyncDependencyAttribute(type='scatter.async.subprocess.SubprocessService')

    #: Default dependencies.
    default_dependencies = ImmutableDict({})

    # def __init__(self, **kwargs):
    #     """
    #
    #     """
    #     name = kwargs.get('name', self.name)
    #     parent = kwargs.get('parent', None)
    #     config = kwargs.get('config', {})
    #     services = kwargs.get('services', ())
    #     attributes = kwargs.get('attributes', {})
    #     dependencies = kwargs.get('dependencies', {})
    #     self.init(name, parent, services, config, attributes, dependencies)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_info = (exc_type, exc_val, exc_tb)
        if all(exc_info):
            self.log.exception('Service encountered an unhandled exception')
        self.stop()

    def __len__(self):
        return len(self.services)

    def __contains__(self, service):
        return service in self.services
    #
    # def __iter__(self):
    #     return iter(self.services)

    @classmethod
    def new(cls, *args, **kwargs):
        service = cls()
        service.init(*args, **kwargs)
        return service

    # def service(self, *sargs, **skwargs):
    #     """
    #
    #     """
    #
    #     def decorator(func):
    #         print 'deco called'
    #         #s = self.child(Service)
    #         @functools.wraps(func)
    #         def wrapper(*args, **kwargs):
    #             print 'wrapper called'
    #             #return s.call(self, func, *args, **kwargs)
    #             return func(*args, **kwargs)
    #
    #         x = self.child(Service)
    #         return x.call()
    #     #    return wrapper
    #
    #     return decorator

    @cached
    def dependency_attributes(self):
        """
        Collection of `scatter.dependency.DependencyAttribute` instances attached
        to this service class.
        """
        return get_instance_descriptors(self, DependencyAttribute)

    @cached
    def service_attributes(self):
        """
        Collection of `scatter.service.ServiceAttribute` instances attached
        to this service class.
        """
        return get_instance_descriptors(self, ServiceAttribute)

    @cached
    def config_attributes(self):
        """
        Collection of `scatter.config.ConfigAttribute` instances attached
        to this service class.
        """
        return get_instance_descriptors(self, ConfigAttribute)

    @cached
    def attributes(self):
        """
        Collection which stores all attributes used to describe a service.
        """
        cls = import_from(self.attribute_collection_class)
        return cls(self.default_attributes)

    @cached
    def config(self):
        """
        Collection which stores all service configuration values.
        """
        return self.config_class(self.default_config)

    @cached
    def services(self):
        """
        Collection which stores child services.
        """
        cls = import_from(self.service_collection_class)
        return cls(self)

    @cached
    def state_machine(self):
        """
        State machine which controls how the service responds to certain events.
        """
        cls = import_from(self.state_machine_class)
        return cls(self)

    def init(self, name=None, process=None, app=None, parent=None, config=None, attributes=None, services=None):
        """
        Initializes the service from scratch or from existing service definition.

        :param name:
        :param process:
        :param app:
        :param parent:
        :param config:
        :param attributes:
        :param services:
        """
        self.process = process
        self.app = app
        self.parent = parent

        self.config.from_object(self.config_attributes)
        self.config.from_object(config)
        self.config.from_file(self.config_file)

        self.id = self.config.get('SERVICE_ID') or urn()
        self.type = resolve_class(self)
        self.fully_qualified_type = resolve_type(self)
        self.name = name or self.config.get('SERVICE_NAME') or self.name or self.type
        self.log = create_logger(self)

        self.attributes.from_object(self.service_attributes)
        self.attributes.from_object(attributes)

        self.services.add(services)

        self.state_machine.init(parent, config, attributes)

    def start(self, *args, **kwargs):
        """
        Start the service and all of its children.
        """
        self.state_machine.start(*args, **kwargs)

    def stop(self, *args, **kwargs):
        """
        Stop the service and all of its children.
        """
        self.state_machine.stop(*args, **kwargs)

    def reload(self, *args, **kwargs):
        """
        Reload the service and all of its children.
        """
        self.state_machine.reload(*args, **kwargs)

    def started(self):
        """
        """
        return self.state_machine.is_started()

    def running(self):
        """
        """
        return self.state_machine.is_running()

    def stopped(self):
        """
        """
        return self.state_machine.is_stopped()

    def join(self, timeout=None):
        """
        Block the caller for the given number of seconds or until the service has stopped.

        :param timeout: Number of seconds to wait for for the service to stop. Defaults to `None`.
        """
        return self.state_machine.stop.wait(timeout)

    def attach(self, service, *args, **kwargs):
        """
        Attach the given service as a child to the current service.

        :param service: Service instance to be treated as a child of this service.
        """
        self.services.add(service)
        service.attached(self, *args, **kwargs)

    def attached(self, parent, *args, **kwargs):
        """
        Action called when the current service is attached to another. If the parent service
        is in a different state than us, we will attempt to playback its service log to catch up.

        :param parent: Service instance we've just attached to.
        """
        self.parent = parent
        #self.state_machine.fast_forward(parent.state_machine, *args, **kwargs)
        self.log.info('Attached to service {0}'.format(parent))
        self.on_attached(parent, *args, **kwargs)

    def detach(self, service, *args, **kwargs):
        """
        Detach the given child service from the current service.

        :param service: Service instance which is a child of this service.
        """
        self.services.remove(service)
        service.detached(self, *args, **kwargs)

    def detached(self, parent, *args, **kwargs):
        """
        Action called when the current service is detached from another.

        :param parent: Service instance we just detached from.
        """
        self.parent = None
        self.log.info('Detatched from service {0}'.format(parent))
        self.on_detached(parent, *args, **kwargs)

    def exports(self):
        """
        Dict of all public service attributes.
        """
        return get_public_attrs(self)

    def child(self, service_cls, *args, **kwargs):
        """
        Create and initialize a new service of the given service class and
        attach it to this service instance.

        :param service_cls:
        :param args:
        :param kwargs:
        """
        service = service_cls.new(parent=self, *args, **kwargs)
        self.attach(service)
        return service

    @classmethod
    def is_abstract(cls):
        """
        Returns True if this service implementation is considered abstract. An abstract service
        is one which explicitly defines an `__abstract__` class attribute equal to `True`. Service
        implementations should mark themselves as abstract if they only provide common functionality
        across concrete instances and don't wish to be created themselves.

        .. note:: Technical Note
        This works because the `__dict__` attribute of class objects will only contain attributes
        which are defined on that class and none which are part of its object hierarchy.
        """
        return is_abstract(cls)

    def is_root(self):
        """
        Returns True if this service the "root" service of this process space.
        """
        return self.parent is None

    def is_app(self):
        """
        Returns True if this service is an "application" service.
        """
        return False
        #return self.parent is not None and self.parent.is_root()

    @classmethod
    @contextlib.contextmanager
    def mock(cls, *args, **kwargs):
        """
        Returns a mock object of this service for the purposes of testing.
        """
        import mock
        with mock.patch(cls.fully_qualified_type, *args, **kwargs) as mocked:
            yield mocked

    @classmethod
    def from_record(cls, **data):
        """
        Creates a new service from the given record data.

        :param data: Service record data which describes how to create it.
        """
        service_type = data.get('fully_qualified_type', resolve_type(cls))
        service_class = import_from(service_type)
        data['services'] = [service_class.from_record(**s) for s in data.get('services', ())]
        return service_class(**data)

    def to_record(self):
        """
        Creates a serializable record which can be used to recreate this service.
        """
        return dict(id=self.id,
                    fully_qualified_type=self.fully_qualified_type,
                    config=self.config,
                    attributes=self.attributes,
                    services=[s.to_record() for s in self.services.all()])

    def initializing(self, *args, **kwargs):
        """
        Initializes this service and all of its children as the action of the `init` state machine transition.
        """
        self.services.from_object(self.dependency_attributes)
        for service in (s for s in self.services.all() if s.state_machine.is_new()):
            service.init(*args, **kwargs)

    def starting(self, *args, **kwargs):
        """
        Starts this service and all of its children as the action of the `start` state machine transition.
        """
        for service in (s for s in self.services.all() if s.state_machine.is_initialized()):
            service.start(*args, **kwargs)

    def stopping(self, *args, **kwargs):
        """
        Stops this service and all of its children as the action of the `stop` state machine transition.

        ..TODO: Service start/stop order should be configurable or use a more expressive dependency hierarchy.

        ..admonition:: Implementation Note
        Child services are stopped in reverse order, meaning the last one started is the first one stopped.
        """
        for service in (s for s in reversed(list(self.services.all())) if s.state_machine.is_running()):
            service.stop(*args, **kwargs)

    def reloading(self, *args, **kwargs):
        """
        Reloads this service and all of its children as the action of the `reload` state machine transition.
        """
        for service in (s for s in reversed(list(self.services.all())) if s.state_machine.is_running()):
            service.reload(*args, **kwargs)

    def on_initializing(self, *args, **kwargs):
        """
        Callback raised when the current service has begun its initialized transition.
        """
        pass

    def on_initialized(self, *args, **kwargs):
        """
        Callback raised when the current service has finished its initialized transition.
        """
        pass

    def on_starting(self, *args, **kwargs):
        """
        Callback raised when the current service has begun its started transition.
        """
        pass

    def on_started(self, *args, **kwargs):
        """
        Callback raised when the current service has finished its started transition.
        """
        pass

    def on_stopping(self, *args, **kwargs):
        """
        Callback raised when the current service has begun its stopped transition.
        """
        pass

    def on_stopped(self, *args, **kwargs):
        """
        Callback raised when the current service has finished its stopped transition.
        """
        pass

    def on_reloading(self, *args, **kwargs):
        """
        Callback raised when the current service has begun its reload transition.
        """
        pass

    def on_reloaded(self, *args, **kwargs):
        """
        Callback raised when the current service has finished its reload transition.
        """
        pass

    def on_attached(self, parent, *args, **kwargs):
        """
        Callback raised when the current service has been attached to another.

        :param parent: Service instance we've been attached to.
        """
        pass

    def on_detached(self, parent, *args, **kwargs):
        """
        Callback raised when the current service has been detached from another.

        :param parent: Service instance we've detached from.
        """
        pass

#
# class ServiceDecorator(object):
#     """
#
#     """
#
#     def __init__(self, *args, **kwargs):
#         pass
#
#     def on_initializing(self, func):
#         def decorator(*args, **kwargs):
#             return func(*args, **kwargs)
#         self.service.on_initializing = decorator
#         return
#
#     # def __init__(self, *args, **kwargs):
#     #     self.service = Service.new(*args, **kwargs)
#     #     self.func = None
#     #     self.on_init = None
#     #
#     # def __call__(self, func, *args, **kwargs):
#     #     if func is not None:
#     #         functools.update_wrapper(self, func)
#     #     self.func = func
#     #     return self
#     #
#     # def __get__(self, instance, owner=None):
#     #     if instance is None:
#     #         return self
#     #     return self.wrapper(instance)
#     #
#     # def initializing(self, func):
#     #     """
#     #     """
#     #     @functools.wraps(func)
#     #     def on_initializing(*args, **kwargs):
#     #         self.service.on_initializing(*args, **kwargs)
#     #         func(*args, **kwargs)
#     #
#     #     self.service.on_initializing = on_initializing
#     #     return self
#     #
#     # def wrapper(self, instance):
#     #     """
#     #
#     #     """
#     #     pass
#
#
# service = ServiceDecorator
#
#
#
# #from scatter import service


# @service()
# def my_service():
#     pass
#
#
# my_service.on_initializing()
# def on_initializing():
#     pass