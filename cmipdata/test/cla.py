"""
Tests of the classes module of cmipdata.

"""

import cmipdata as cd
import os
import cmip_testing_tools as ctt

def test(directory, sourcefiles, cwd):
    """ Makes a file in /testdata/ name testclasses_file.txt whcih has the ensemble info
        after using match ensembles and match_realizations
    """
    # first change to a scratch dir and link in test data. The paths are CCCma specific.
    ctt.loadtestfiles(directory,sourcefiles)
    f = cwd + '/testdata/testclasses_file.txt'

    # =========================================================================
    #     mkensemble
    # =========================================================================
    fp = '*historical*'
    ens = cd.mkensemble(fp, prefix='')
    ens.fulldetails_tofile(f)

    # Create a second cmipdata ensemble
    fp2 = '*ts*'
    ens2 = cd.mkensemble(fp2, prefix='')
    ens.fulldetails_tofile(f)
    # =========================================================================
    #     match_ensembles
    # =========================================================================
    print 'Matching ensembles...'
    enso1, enso2 = cd.match_ensembles(ens, ens2)
    enso1.sinfo()
    enso2.sinfo()
    ens.fulldetails_tofile(f)
    # =========================================================================
    #     match_realizations
    # =========================================================================
    print 'Matching realizations...'
    ensem1, ensem2 = cd.match_realizations(ens, ens2)
    ensem1.sinfo()
    ensem2.sinfo()
    ens.fulldetails_tofile(f)
