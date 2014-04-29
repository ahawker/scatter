"""
    scatter.main
    ~~~~~~~~~~~~

    Entry point for scatter command line applications.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('main',)


import sys

from scatter.cli import scatter_parser, control_parser
from scatter.process import Process, Daemon


def main(argv):
    """

    """
    # Consume command-line arguments.
    parser = scatter_parser()
    args = parser.parse_args(argv)

    if args.help:
        parser.print_help()
        return 0

    #config = dict(debug=())


    # ...
    process = Daemon if args.daemonize else Process
    process.config.from_args(args)


def run(cls, *args, **kwargs):
    """
    """
    with cls.new(*args, **kwargs) as process:
        process.log.info('Service running')
        process.join()


if __name__ == '__main__':
    main(sys.argv)