"""
    scatter.__main__
    ~~~~~~~~~~~~~~~~

    Run scatter as a module.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""


def main(argv):
    from main import main
    return main(argv)


if __name__ == '__main__':
    import sys
    main(sys.argv)
