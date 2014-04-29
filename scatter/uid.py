"""
    scatter.uid
    ~~~~~~~~~~~

    Generate identifiers.

    :copyright: (c) 2014 Andrew Hawker.
    :license: ?, See LICENSE file.
"""
__all__ = ('urn', 'sha1', 'uid')


import hashlib
import random

from uuid import uuid4


def urn():
    return uuid4().urn


def sha1(obj):
    return int(hashlib.sha1(obj).hexdigest(), 16)


def uid(bits=160):
    return sha1(str(random.getrandbits(bits)))
