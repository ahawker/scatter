"""
    setup.py
    ~~~~~~~~

    Install it, yo!
"""

import scatter

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name=scatter.__name__,
    version=scatter.__version__,
    description='Applications across borders.',
    long_description=open('README.md').read(),
    author='Andrew Hawker',
    author_email='andrew.r.hawker@gmail.com',
    url='https://github.com/scatter/scatter',
    license=open('LICENSE.md').read(),
    package_dir={'scatter': 'scatter'},
    packages=['scatter'],
    test_suite='tests',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    )
)
