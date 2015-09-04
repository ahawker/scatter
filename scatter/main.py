"""
    scatter.main
    ~~~~~~~~~~~~

    Entry point for scatter command line applications.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('main',)

from gevent import monkey
monkey.patch_all()


import sys

from scatter.cli import create_scatter_parser
from scatter.importer import import_from
from scatter.process import Process, Daemon


def func(service):
    print 'FKFDJKLSJKLFS'
    service.log.error('OLOLOLOOLOLOL')


def main(argv):
    """
    Main entry point for running scatter processes.

    :param argv: List containing command line arguments.
    """
    # Consume command-line arguments.
    parser = create_scatter_parser()
    args = parser.parse_args(argv)

    # Configure which process class to use, taking into account custom user defined process types.
    process_factory = Daemon if args.daemonize else Process
    if args.process:
        process_factory = import_from(args.process)

    # Load service(s) classes to run in this process.
#    services = [import_from(service)() for service in args.service]

    # Mark all arguments as uppercase so they auto-load into configuration.
    config = dict((k.upper(), v) for k, v in vars(args).items())

    proc = process_factory.new(config=config)
    for s in args.service:
        x=proc.child(import_from(s))
    proc.start()
    print proc.config
    proc.log.info('Process running!')
    x.spawn(func)
    x.spawn(func)
    proc.join(5)
    proc.stop()
    #with proc as proc:
    #    proc.join(5)
    #services = [import_from(service)() for service in args.service]
    #proc.a

#    return process_factory.run(config=config, services=services)


if __name__ == '__main__':
    main(sys.argv[1:])