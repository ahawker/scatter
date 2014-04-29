"""
    scatter.cli
    ~~~~~~~~~~~

    Implements command-line parsers for scatter tools.
"""
__all__ = ('scatter_parser', 'control_parser')


import argparse
import scatter


def scatter_parser():
    """
    Builds :class: `~argparse.ArgumentParser` for consuming scatter command-line arguments.
    """
    parser = argparse.ArgumentParser('scatter', description='')
    parser.add_argument('-c', '--config',
                        action='config_file',
                        help='configuration file to load')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s {0}'.format(scatter.__version__))
    parser.add_argument('-d', '--daemonize',
                        action='daemonize',
                        help='daemonize scatter process')
    parser.add_argument('-u', '--user',
                        action='user',
                        help='run process as this user (or uid)')
    parser.add_argument('-g', '--group',
                        action='group',
                        help='run process as this group (or gid)')
    parser.add_argument('-r', '--rundir',
                        action='rundir',
                        help='run process in this directory')
    parser.add_argument('-d', '--debug',
                        action='debug',
                        help='enable process debug mode')
    parser.add_argument('-a', '--app',
                        action='app',
                        help='')
    return parser


def control_parser():
    """

    """
    return None