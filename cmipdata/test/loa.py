"""
Tests of the loading_tools module of cmipdata.

"""

import cmipdata as cd
import os
import hashlib
import cmip_testing_tools as ctt


def test_loadingtools(directory, sourcefiles, var):
    """ Loads the data from a set of files 
    """
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    data = hashlib.sha1(cd.loadfiles(ens,var)['data']).hexdigest()
    return {var: data}
