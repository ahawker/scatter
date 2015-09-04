"""
    scatter.log
    ~~~~~~~~~~~

    Implements a logger which is attached to every :class: `~scatter.service.Service` instance.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('create_logger',)


import logging

from scatter.meta import resolve_class

DEFAULT_LOG_LEVEL = logging.INFO


def create_logger(service):
    """
    Create a logger which extends the :class: `~logging.Logger` to support service context.
    """
    class ScatterLogger(logging.getLoggerClass()):
        """
        ScatterLogger is an extension of the :class: `~logging.Logger` stdlib logger which
        automatically exposes service context into the :class: `~logging.LogRecord` so it can
        be optionally consumed by the :class: `~logging.Formatter` or :class: `~logging.Handler`.
        """

        @classmethod
        def file_descriptors(cls):
            """
            Helper function which returns all file descriptors currently opened by the logging
            subsystem.

            ..note:: Usage
            This is used by :class: `~scatter.process.Daemon` to know which file descriptors it should
            leave open when forking the process.
            """
            file_handlers = (h for h in logging._handlerList if isinstance(h, logging.FileHandler))
            return [handler.stream.fileno() for handler in file_handlers]

        def getEffectiveLevel(self):
            """
            Modify the logging level based on standard logging rules or custom service toggles.
            """
            if self.level == 0 and service.debug:
                return logging.DEBUG

            if service.log_level is not None and self.level != service.log_level:
                self.setLevel(service.log_level)

            return super(ScatterLogger, self).getEffectiveLevel()

        def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
            """
            Modify the standard :class: `~logging.LogRecord` creation to automatically inject
            service specific context into the `extras` field.
            """
            if extra is None:
                extra = {}

            extra['service_name'] = service.name
            extra['service_id'] = service.id
            extra['service_type'] = service.type

            return super(ScatterLogger, self).makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra)

        def child(self, service):
            """
            Return a :class: `~scatter.log.ScatterLogger` instance attached as a child
            to this logger keyed by class name.
            """
            #suffix = resolve_class(obj)
            print 'CHILD SUFFIX {0}'.format('.'.join((self.name, service.id)))
            child = super(ScatterLogger, self).getChild(service.id)
            child.__class__ = ScatterLogger
            child.propagate = True
            return child

        @staticmethod
        def shutdown():
            """
            Helper function which exposes the ability to shutdown the logging subsystem from
            every instance of the logger.

            ..note:: Usage
            The "root" service should be the only service calling this. If you're calling this
            directory from a custom app or service, you're going to have a bad time.
            """
            logging.shutdown()

    # Only configure logger when its a "root" logger, otherwise just attach it as a child logger.
    # A child logger should inherit its ancestors formatter and handler configuration.
    #if service.is_root() or service.is_app():
    #    print '{0} is root or app!'.format(service)
        # Configure Scatter log handler.
    formatter = (service.log_formatter_class or logging.Formatter)(service.log_format)
    handler = (service.log_handler_class or logging.StreamHandler)()
    handler.setFormatter(formatter)

    # Configure Scatter logger.
    logger = logging.getLogger(service.id)
    logger.__class__ = ScatterLogger
    logger.addHandler(handler)
    logger.setLevel(service.log_level)
    logger.propagate = False
    #else:
    #    logger = service.parent.log.child(service)

    return logger



