"""
    scatter.process
    ~~~~~~~~~~~~~~~

    Implementation of services which are analogous to an operating system process and
    the root of the service hierarchy

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('Process', 'Daemon')


import daemon
import fcntl
import grp
import os
import pwd
import signal

from scatter.config import ConfigAttribute
from scatter.service import Service, ServiceAttribute


class Pidfile(object):
    """
    Representation of a .pid file which stores the pid of a daemon process. Manages
    the file through a context manager which to be consumed by the :class: `~daemon.DaemonContext` of
    a :class: `~scatter.process.Daemon`.
    """

    def __init__(self, path):
        if not path:
            raise ValueError('path must be set')
        self.path = path
        self.pidfile = None

    def __enter__(self):
        self.pidfile = open(self.path, 'a+')
        try:
            fcntl.flock(self.pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise RuntimeError('Pidfile {0} already in use.'.format(self.path))
        else:
            self.pidfile.seek(0)
            self.pidfile.truncate()
            self.pidfile.write(str(os.getpid()))
            self.pidfile.flush()
            self.pidfile.seek(0)
            return self.pidfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pidfile.close()
        os.remove(self.path)


class Process(Service):
    """
    Service analogous to an operating system process.
    """

    #: Set the process group by name or its id.
    group = ConfigAttribute()

    #: Set the current working directory of the process.
    rundir = ConfigAttribute()

    #: Set the process file mode creation mask.
    umask = ConfigAttribute()

    #: Set the process user by name or its id.
    user = ConfigAttribute()

    #: Get the process working directory. Configurable
    # by config key `RUNDIR` or `self.rundir`.
    cwd = ServiceAttribute()

    #: Get the process group id. Configurable
    # by config key `GROUP` or `self.group`.
    gid = ServiceAttribute()

    #: Get the process id.
    pid = ServiceAttribute()

    #: Get the process user id. Configurable
    # by the config key `USER` or `self.user`.
    uid = ServiceAttribute()

    def __init__(self):
        self.cwd = os.getcwd()
        self.gid = os.getegid()
        self.pid = os.getpid()
        self.uid = os.geteuid()
        self.msk = os.umask(0)
        self.env = os.environ.copy()

    def on_initializing(self, *args, **kwargs):
        """
        """
        # Working directory and default process file permissions.
        if self.rundir is not None:
            os.chdir(self.rundir)
            self.cwd = os.getcwd()
        if self.umask is not None:
            self.msk = os.umask(self.umask)

        # Change process group.
        if self.group is not None:
            group = grp.getgrnam(self.group)
            self.gid = group.gr_gid
            os.setgid(self.gid)

        # Change process user, which implicitly changes to its group.
        if self.user is not None:
            user = pwd.getpwnam(self.user)
            self.uid = user.pw_uid
            self.gid = user.pw_gid
            os.setgid(self.gid)
            os.setuid(self.uid)

    def on_stopped(self, *args, **kwargs):
        """
        """
        self.log.shutdown()

    def on_reloading(self, *args, **kwargs):
        """
        """
        self.config.from_file(self.config_file)


class Daemon(Process):
    """
    Service analogous to an operating system process which daemonizes itself on startup.
    """

    #: Set the file path of where to create/save a .pid file which
    # stores the daemon process id.
    pidfile = ConfigAttribute()

    def __init__(self):
        super(Daemon, self).__init__()
        self.daemon = daemon.DaemonContext()

    def __enter__(self):
        self.daemon.__enter__()
        super(Daemon, self).__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super(Daemon, self).__exit__(exc_type, exc_val, exc_tb)
        return self.daemon.__exit__(exc_type, exc_val, exc_tb)

    def on_initializing(self, *args, **kwargs):
        """
        """
        super(Daemon, self).on_initializing(*args, **kwargs)
        if self.pidfile is None:
            self.pidfile = os.path.expanduser('~/.{0}.pid'.format(self.name))

    def on_initialized(self, *args, **kwargs):
        """
        """
        self.daemon = daemon.DaemonContext(uid=self.uid,
                                           gid=self.gid,
                                           umask=self.msk,
                                           working_directory=self.cwd,
                                           pidfile=Pidfile(self.pidfile),
                                           files_preserve=self.log.file_descriptors,
                                           signal_map={
                                               signal.SIGTERM: self.stop,
                                               signal.SIGHUP: self.reload,
                                           })