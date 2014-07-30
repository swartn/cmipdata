"""
A series of tests on the preprocessing_tools module of cmipdata.
"""

import cmipdata as cd
import os

# first change to a scratch dir and link in test data. The paths are CCCma specific.
os.chdir('/home/ncs/ra40/cmipdata/test_preprocessing_tools')
os.system('rm -f *.nc')

# Load in surface temperature data for two models. More could be used, but slower.
os.system('ln -s /ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CanESM2*historical*.nc .')
os.system('ln -s /ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CanESM2*rcp45*.nc .')
os.system('ln -s /ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CCSM4*historical*.nc .')
os.system('ln -s /ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CCSM4*rcp45*.nc .')

# Create a cmipdata ensemble 
filepattern = 'ts_Amon*'
ens = cd.mkensemble(filepattern)

# print out info on the ensemble
ens.fulldetails()
ens.sinfo()

#=========================================================================
#     cat_exp_slices
#=========================================================================
ens = cd.cat_exp_slices(ens)
ens.fulldetails()

#=========================================================================
#     cat_experiments
#=========================================================================
ens = cd.cat_experiments(ens, 'ts', exp1_name='historical', exp2_name='rcp45')
ens.fulldetails()

#=========================================================================
#     zonmean
#=========================================================================
ens = cd.zonmean(ens,delete=False)
ens.fulldetails()

#=========================================================================
#     remap
#=========================================================================
ens = cd.remap(ens, remap='r1x180')
ens.fulldetails()

#=========================================================================
#     time_slice
#=========================================================================
ens = cd.time_slice(ens, start_date='1979-01-01', end_date='2013-12-31')
ens.fulldetails()

#=========================================================================
#     time_anomaly
#=========================================================================
ens = cd.time_anomaly(ens, start_date='1980-01-01', end_date='2010-12-31')
ens.fulldetails()

#=========================================================================
#     ens_stats
#=========================================================================
cd.ens_stats(ens, 'ts')

#=========================================================================
#     my_operator
#=========================================================================
# try to reproduce the above (after cat, before ens_stats: 
#i.e. zonmean, remap, time_slice, time_anomaly) in one step:
ens = cd.mkensemble(filepattern + '197901-201312.nc')
cd.del_ens_files(ens) # Get rid of the processed files.
ens = cd.mkensemble(filepattern)
my_cdo_str = 'cdo remapdis,r1x180 -zonmean -seldate,1979-01-01,2013-12-31\
             -sub {infile} -timmean -seldate,1991-01-01,2000-12-31 {infile}\
             {outfile}'
ens = cd.my_operator(ens, my_cdo_str, output_prefix='test_', delete=False)
cd.ens_stats(ens, 'ts')



