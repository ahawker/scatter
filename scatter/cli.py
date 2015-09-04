"""
    scatter.cli
    ~~~~~~~~~~~

    Implements command-line parsers for scatter tools.
"""
__all__ = ('create_scatter_parser',)


import argparse
import scatter
import sys


class ScatterParser(argparse.ArgumentParser):
    """
    Extend :class: `~argparse.ArgumentParser` to automatically show the help/usage on error cases.
    """

    def error(self, message):
        sys.stderr.write('error: {0}\n'.format(message))
        self.print_help()
        sys.exit(2)


def control_command_parser(parser):
    """
    Build and attach parser for consuming `scatter control` command-line arguments.

    :param parser: Command parser to attach ourselves.
    """
    parser.add_argument('service',
                        nargs='+',
                        action='store',
                        help='service(s) to control')
    parser.add_argument('action',
                        choices=('start', 'stop', 'reload', 'status'),
                        help='action to run against service')
    parser.add_argument('-p', '--pidfile',
                        action='store',
                        dest='pidfile',
                        help='pidfile for scatter process to control')
    parser.add_argument('-c', '--config',
                        action='store',
                        dest='config',
                        help='config file for scatter process to control')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s {0}'.format(scatter.__version__))
    return parser


def service_command_parser(parser):
    """
    Build and attach parser for consuming `scatter service` command-line arguments.

    :param parser: Command parser to attach ourselves.
    """
    parser.add_argument('service',
                        nargs='+',
                        action='store',
                        help='service(s) to run')
    parser.add_argument('-c', '--config',
                        action='store',
                        dest='config',
                        help='configuration file to load')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s {0}'.format(scatter.__version__))
    parser.add_argument('-b', '--background',
                        action='store_true',
                        dest='daemonize',
                        help='run in daemon process')
    parser.add_argument('-u', '--user',
                        action='store',
                        dest='user',
                        help='run process as this user (or uid)')
    parser.add_argument('-g', '--group',
                        action='store',
                        dest='group',
                        help='run process as this group (or gid)')
    parser.add_argument('-r', '--rundir',
                        action='store',
                        dest='rundir',
                        help='run process in this directory')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        dest='debug',
                        help='enable process debug mode')
    parser.add_argument('-t', '--test',
                        action='store_true',
                        dest='test',
                        help='enable process test mode')
    parser.add_argument('-p', '--process',
                        action='store',
                        dest='process',
                        help='process service to use')
    parser.add_argument('-n', '--name',
                        action='store',
                        dest='service_name',
                        help='set process service name')
    parser.add_argument('-i', '--id',
                        action='store',
                        dest='service_id',
                        help='set process service id')
    return parser


def create_scatter_parser():
    """
    Create :class: `~scatter.cli.ScatterParser` for parsing command line arguments
    for managing scatter processes.
    """
    parser = ScatterParser('scatter', description='Manage scatter processes')

    # Create `command` subparser and attach known commands.
    commands = parser.add_subparsers(dest='command', help='Scatter command')
    service_command_parser(commands.add_parser('service', help='Service options'))
    control_command_parser(commands.add_parser('control', help='Control options'))

    return parser