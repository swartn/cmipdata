import cmipdata as cd
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib as mpl
# set font size
plt.close('all')
plt.ion()
import os
os.system( 'rm -rf /tmp/cdo*') # clean out tmp to make space for CDO processing.

# Define the location of the data
rean_data_path = '/HOME/ncs/data/reanalyses/'
infile = rean_data_path +  'CFSR_slp.mon.mean.nc'

# get out the latitudes
nc = Dataset( infile , 'r' )
slp = nc.variables[ 'slp' ]
ind = [ j for j, dim in enumerate(slp.dimensions) if dim.lower().startswith('lat') ]
lat = cd.loadvar(infile, slp.dimensions[ind[0]])

# test timnean, startdate, zonmean and remap
print "timnean, startdate, remap and zonmean"
slpclim = cd.loadvar( infile, varname='slp', remap='r180x1', start_date='1979-01-01', end_date='2009-12-31', timmean=True, zonmean=True)
print slpclim.shape

# test timnean, startdate and remap
print "timnean, startdate and remap"
slpclim = cd.loadvar( infile, 'slp', remap='r360x180', start_date='1979-01-01', end_date='2009-12-31', timmean=True)
print slpclim.shape

# test timnean, startdate and zonmean
print "timnean, startdate and zonmean"
slpclim = cd.loadvar( infile, 'slp', start_date='1979-01-01', end_date='2009-12-31', timmean=True, zonmean=True)
print slpclim.shape

# test timnean, zonmean and remap
print "timnean, zonmean and remap"
slpclim = cd.loadvar( infile, 'slp', remap='r180x1', timmean=True, zonmean=True)
print slpclim.shape

# test startdate, zonmean and remap
print "startdate, remap and zonmean"
slpclim = cd.loadvar( infile, varname='slp', remap='r180x1', start_date='1979-01-01', end_date='2009-12-31', zonmean=True)
print slpclim.shape

# test timnean and remap
print "timnean remap"
slpclim = cd.loadvar( infile, varname='slp', remap='r360x180', timmean=True)
print slpclim.shape

# test startdate and remap
print "startdate and remap"
slpclim = cd.loadvar( infile, 'slp', remap='r360x180', start_date='1979-01-01', end_date='2009-12-31')
print slpclim.shape

# test timnean, startdate, 
print "timnean and startdate"
slpclim = cd.loadvar( infile, varname='slp', start_date='1979-01-01', end_date='2009-12-31', timmean=True)
print slpclim.shape

# test timnean and zonmean
print "timneanand zonmean"
slpclim = cd.loadvar( infile, varname='slp', timmean=True, zonmean=True)
print slpclim.shape

# startdate and zonmean
print "startdate and zonmean"
slpclim = cd.loadvar( infile, varname='slp', start_date='1979-01-01', end_date='2009-12-31', zonmean=True)
print slpclim.shape

# test zonmean and remap
print "remap and zonmean"
slpclim = cd.loadvar( infile, varname='slp', remap='r180x1', zonmean=True)
print slpclim.shape

# test  remap
print "remap"
slpclim = cd.loadvar( infile, varname='slp', remap='r360x180')
print slpclim.shape

# load timmean
print "timmean"
slpclim = cd.loadvar( infile, varname='slp', timmean=True )
print slpclim.shape

# startdate 
print "startdate"
slpclim = cd.loadvar( infile, varname='slp', start_date='1979-01-01', end_date='2009-12-31')
print slpclim.shape

# load zonmean
print "zonmean"
slpclim = cd.loadvar( infile, varname='slp', zonmean=True )
print slpclim.shape

# a vanilla load
print "load"
slpclim = cd.loadvar( infile, varname='slp' )
print slpclim.shape


plt.plot( lat, slpclim[0,:,0])

dimensions = cd.get_dimensions( infile, 'slp')
print dimensions.keys()



