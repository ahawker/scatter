"""
    scatter.ext
    ~~~~~~~~~~~

    Package name which to alias external extensions under the root `scatter` namespace.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""


def install():
    """
    Install the :class: `~scatter.importer.ExtensionImporter` to automatically
    alias extensions from `scatter_*` to `scatter.ext.*`.
    """
    from scatter.importer import ExtensionImporter
    importer = ExtensionImporter('scatter_', __name__)
    importer.register()


install()
del install