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
    print 'Could not import loading_tools. Check that the correct versions of cdo, numpy, and netCDF4 are installed.'

# Requires matplotlib
try:
    from plotting_tools import *
except ImportError:
    print 'Could not import plotting_tools. Check that the correct versions of cdo, numpy, scipy, Basemap, matplotlib and netCDF4 are installed.'
