###
"""
cmipdata
========

"""
import os
import glob

# __all__ = ["join_exp_slice", "zonmean", "loaddata", "match_exp", "remap_timelim", "remap_cmip_nc" ,"mload1d", "climatology", "areaint"]

from classes import *
from preprocessing_tools import *

# Requires cdo python bindings and netcdf4
try:
    from loading_tools import *
except ImportError:
    pass

# Requires matplotlib
try:
    from plotting_tools import *
except ImportError:
    pass
