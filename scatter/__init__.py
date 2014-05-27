"""
    scatter
    ~~~~~~~

    Erecting a dispenser.

    :copyright: (c) 2013 by Andrew Hawker.
    :license: See LICENSE for more details.
"""
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'
__name__ = 'scatter'
__license__ = '???'


import itertools

try:
    from __version__ import __version__
except ImportError:
    pass
else:
    __version__ = __version__


from . import app
from .app import *
from . import codec
from .codec import *
from . import config
from .config import *
from . import descriptors
from .descriptors import *
from . import exceptions
from .exceptions import *
from . import protocol
from .protocol import *
from . import proxy
from .proxy import *
from . import service
from .service import *
from . import state
from .state import *
from . import structures
from .structures import *

__all__ = list(itertools.chain(app.__all__,
                               codec.__all__,
                               config.__all__,
                               descriptors.__all__,
                               exceptions.__all__,
                               protocol.__all__,
                               proxy.__all__,
                               service.__all__,
                               state.__all__,
                               structures.__all__))
