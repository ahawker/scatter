"""
    scatter.importer
    ~~~~~~~~~~~~~~~~

    Custom importing of python objects.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('import_from', 'PackageImporter', 'ExtensionImporter')


import importlib
import inspect
import os
import pkg_resources
import sys

from scatter.descriptors import cached


def import_from(obj, silent=False):
    """
    Import a module/class from the given object. Expected to be a fully qualified
    string to import from or a Class object.

    :param obj: String which represents a fully qualified type to import.
    :param silent: Flag to indicate if we should re-raise any ImportError.
    :return:
    """
    if inspect.isclass(obj):
        return obj

    obj = str(obj)

    try:
        # No import hierarchy, importing a top level module.
        if '.' not in obj:
            return importlib.import_module(obj)

        # Import module and return specified attribute.
        mod, cls = obj.rsplit('.', 1)
        module = importlib.import_module(mod)
        try:
            return getattr(module, cls)
        except AttributeError:
            raise ImportError('{0} not found'.format(obj))
    except ImportError:
        if not silent:
            raise


class PackageImporter(object):
    """

    """

    #:
    #:
    entry_name = 'ext'

    #:
    #:
    entry_enabled_name = 'ENABLED'

    def __init__(self, service, ext_prefix='scatter'):
        self.service = service
        self.ext_prefix = ext_prefix

    @cached
    def entry_points(self):
        """
        """
        def _iter_entry_points():
            """
            Helper function which yields back valid scatter extension packages. A valid package matches
            the set `ext_prefix` and exports an entry_point in its `setup.py` named `package`. The
            `package` value should be the fully qualified type string it should be imported under.
            Ex: `scatter.ext.my_extension`
            """
            for dist in (d for d in pkg_resources.working_set if d.project_name.startswith(self.ext_prefix)):
                for entry_point in dist.get_entry_map(None).values():
                    package = entry_point.get(self.entry_name)
                    if package is None:
                        msg = 'Extension package {0} is missing entry point.'.format(dist.project_name)
                        self.service.log.warning(msg)
                        continue
                    yield package

        return list(_iter_entry_points())

    def load(self, silent=False):
        """
        """
        for package in self.entry_points:
            package_name = package.dist.project_name
            try:
                # Attempt to load our extension package and check its status.
                imported = package.load()
                enabled = getattr(imported, self.entry_enabled_name, None)

                # Extension packages must expose an attribute to inform us of enabled/disabled status.
                if enabled is None:
                    msg = 'Extension package {0} must expose {1} attribute to be enabled.'
                    raise ImportError(msg.format(package_name, self.entry_enabled_name))

                # Extension package successfully loaded and has valid entry point.
                enabled = bool(enabled)
                msg = 'Extension package {0} is {1}'.format(package_name, 'enabled' if enabled else 'disabled')
                self.service.log.info(msg)
            except ImportError:
                if not silent:
                    raise


class ExtensionImporter(object):
    """
    A custom import hooks for scatter extensions (scatter.ext.*) as defined in PEP 302 [1].

    See `scatter.ext.__init__.py` for more details.

    [1] http://www.python.org/dev/peps/pep-0302/
    """

    def __init__(self, ext_prefix, ext_module):
        """
        Create a custom import loader to redirect imports of a specific path.

        :param ext_prefix: String prefix of modules/packages to load as extensions.
        :param ext_module: Fully-qualified path to import extensions under.
        """
        self.ext_prefix = ext_prefix
        self.ext_module = ext_module
        self.ext_module_depth = ext_module.count('.') + 1

    def register(self):
        """
        Add this custom importer to the `sys.meta_path` collection of importers.
        """
        if self in sys.meta_path:
            return
        sys.meta_path.append(self)

    def find_module(self, fullname, path=None):
        """
        Returns this `ExtensionImporter` instance when the import system is looking to load a module
        contains our registered prefix.

        :param fullname: Fully qualified module name.
        :param path: Package path of module or None if top-level import.
        """
        if fullname.startswith(self.ext_module):
            return self

    def load_module(self, fullname):
        """
        Returns the loaded scatter extension module or raises an `ImportError` on error.

        :param fullname: Fully qualified module name.
        """
        # Module has already been loaded
        module = sys.modules.get(fullname, None)
        if module is not None:
            return module

        # Build extension module name by substituting in our ext_module in the fully qualified import path.
        module_name = fullname.split('.', self.ext_module_depth)[self.ext_module_depth]
        full_module_name = self.ext_prefix + module_name

        # Try and import the extension.
        try:
            __import__(full_module_name)
        except ImportError:
            exc_type, exc_value, traceback = sys.exc_info()

            # Remove module entry if this happened to be a recursive import.
            if full_module_name in sys.modules:
                del sys.modules[module_name]

            # Re-raise this exception if we successfully found the extension
            # but failed to import it.
            if _is_module_in_traceback(full_module_name, traceback):
                raise exc_type, exc_value, traceback

            # Failed to import the extension, so we must raise an ImportError to notify Python import system.
            raise ImportError('No module named {0}'.format(module_name))
        else:
            module = sys.modules[fullname] = sys.modules[full_module_name]
            return module


def _is_module_in_traceback(module_name, traceback):
    """
    Returns True if the raised ImportError originated from a call stack which includes
    the given module name.

    :param module_name: Name of module we're checking the call stack for.
    :param traceback: Traceback of an ImportError we're examining.
    """
    # Traverse call stack looking for the extension module that's being imported.
    while traceback is not None:
        if _is_module_in_traceback_frame(module_name, traceback.tb_frame):
            return True
        traceback = traceback.tb_next
    return False


def _is_module_in_traceback_frame(module_name, frame):
    """
    Returns True if the given module name, was part of the call stack in the given traceback.

    :param module_name: Name of a module we're checking as the originator of this traceback frame.
    :param frame: Frame object of a traceback to examine.
    """
    # Compare module which generated traceback frame to our target module.
    frame_module_name = frame.f_globals.get('__name__', '')
    if module_name == frame_module_name:
        return True

    # Built file path based on module name.
    # Python imports are dot-separated which maps directly to a slash-separated filepath.
    module_filename = module_name.replace('.', os.path.sep)

    # Check if the traceback frame came from this module or a like named package.
    module_path = '{0}.py'.format(module_filename)
    package_path = os.path.sep.join((module_filename, '__init__.py'))

    # Compare path of traceback frame to our target import as both a module and package.
    frame_filename = os.path.abspath(frame.f_code.co_filename)
    return any((module_path in frame_filename, package_path in frame_filename))
