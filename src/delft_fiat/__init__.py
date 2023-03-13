##################################################
# Organisation: Deltares
##################################################
# Author: B.W. Dalmijn
# E-mail: brencodeert@outlook.com
##################################################
# License: MIT license
#
#
#
#
##################################################
import importlib.util
import warnings

from .version import __version__
from .main import FIAT

# if not importlib.util.find_spec("PySide2"):
#     warnings.warn("PySide2 is not installed in this environment -> ui is not callable")
# else:
#     from .gui import *
