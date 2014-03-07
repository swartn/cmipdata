import glob
import slice_nc as slice
import datetime
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset,num2date,date2num
import cdo as cdo; cdo = cdo.Cdo() # recommended import
plt.close('all')
plt.ion()

def plot_ens():
    filenames = sorted( glob.glob("rm_*.nc") )

    modelnames = [ filename.split( '_' )[2] for filename in filenames ]
    uniq_mods = modelnames
    print
    print "--------------------"
    print "Number of models: " , len( uniq_mods )
    print "--------------------"
    print

    # set up the matrix
    ofile = filenames[0]
    nc = Dataset( ofile , 'r' )
    fgco2 = nc.variables['fgco2']
    sz = list( fgco2.shape )
    sz.append( len( uniq_mods ) )
    #fgco2_mat = np.empty( sz )

    for k, cfile in enumerate( filenames ):
      if k<2:
	  ofile = cfile
	  cfile = cfile.replace('rm_','')
	  varname = cfile.split('_')[0]
	  mod = cfile.split( '_' )[2]
	  realm = cfile.split('_')[1]
	  ensmember = cfile.split('_')[4]
	  exp = cfile.split('_')[3]

	  nc = Dataset( ofile , 'r' )
	  lon = nc.variables['lon']
	  lat = nc.variables['lat']
	  time_nc = nc.variables['time']
	  the_times = time_nc[...]
	  dates_nc = num2date( the_times, time_nc.units, time_nc.calendar )
	  
	  print mod, fgco2.shape

	  #mask = fgco2 == fgco2._FillValue
	  #fgco2 = np.ma.MaskedArray( fgco2 , mask = mask )
	  #fgco2_mat[ : , : , : , k ] = fgco2
	  #xm_fgco2 = np.mean ( fgco2 , 2 )
	  xm_fgco2 = cdo.zonmean(input=ofile,returnMaArray ='fgco2')
	  plt.plot( lat , np.mean( xm_fgco2 , 0 ) ,'-', color = '0.25', alpha=0.25) # plot the time mean
    
    plt.plot( [ -90, 90 ] , [0 , 0] , 'k--') 
    plt.xlim( [ -90, 90 ] )
    plt.grid()

    
plot_ens()
