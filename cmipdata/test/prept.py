"""
A series of tests on the preprocessing_tools module of cmipdata.
"""

import cmipdata as cd
import os
import cmip_testing_tools as ctt

# =========================================================================
#     starting files
# =========================================================================
def test_starting_files(directory, sourcefiles):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    data = ctt.sha(ens)
    return data
    
# =========================================================================
#     cat_exp_slices
# =========================================================================
def test_cat_exp_slices(directory, sourcefiles):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.cat_exp_slices(ens)
    data = ctt.sha(ens)                
    return data

# =========================================================================
#     cat_experiments
# =========================================================================
def test_cat_experiments(directory, sourcefiles, var, e1name, e2name):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.cat_experiments(ens, var, exp1_name=e1name, exp2_name=e2name)
    data = ctt.sha(ens)    
    return data

# =========================================================================
#     zonmean
# =========================================================================
def test_zonal_mean(directory, sourcefiles):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.zonmean(ens, delete=True)
    data = ctt.sha(ens)   
    return data

# =========================================================================
#     remap
# =========================================================================
def test_remap(directory, sourcefiles):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.remap(ens, remap='r1x180')
    data = ctt.sha(ens)    
    return data

# =========================================================================
#     time_slice
# =========================================================================
def test_time_slice(directory, sourcefiles, sd, ed):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.time_slice(ens, start_date=sd, end_date=ed)
    data = ctt.sha(ens)    
    return data

# =========================================================================
#     time_anomaly
# =========================================================================
def test_time_anomaly(directory, sourcefiles, sd, ed):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.time_anomaly(ens, start_date=sd, end_date=ed, delete=True)
    ens.fulldetails()
    data = ctt.sha(ens)    
    return data

# =========================================================================
#     ens_stats
# =========================================================================
def test_ens_stats(directory, sourcefiles, var):
    ctt.loadtestfiles(directory, [sourcefiles[0]])
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    cd.ens_stats(ens, var)
    filepattern = 'ENS*'
    ens = cd.mkensemble(filepattern)    
    data = ctt.sha(ens)   
    return data

# =========================================================================
#     my_operator
# =========================================================================
def test_my_operator(directory, sourcefiles, var, e1name, e2name):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.cat_experiments(ens, var, exp1_name=e1name, exp2_name=e2name)   
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    my_cdo_str = 'cdo remapdis,r1x180 -zonmean -seldate,1950-01-01,2000-12-31\
             -sub {infile} -timmean -seldate,1950-01-01,2000-12-31 {infile}\
             {outfile}'
    ens = cd.my_operator(ens, my_cdo_str, output_prefix='test_', delete=True)
    data = ctt.sha(ens)   
    return data
    
# =========================================================================
#     areaint
# =========================================================================
def test_areaint(directory, sourcefiles):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.areaint(ens)
    data = ctt.sha(ens)    
    return data

# =========================================================================
#     areamean
# =========================================================================
def test_areamean(directory, sourcefiles):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.areamean(ens)
    data = ctt.sha(ens)    
    return data
    
# =========================================================================
#     climatology
# =========================================================================
def test_climatology(directory, sourcefiles):
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.climatology(ens)
    data = ctt.sha(ens)    
    return data
