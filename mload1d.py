import os
import numpy as np 

from netCDF4 import Dataset
import cdo as cdo; cdo = cdo.Cdo() # recommended import
os.system( 'rm -rf /tmp/cdo*') # clean out tmp to make space for CDO processing.

def mload1d(ifiles, varname, tmean=''):
        """  
            Load a netcdf variable "varname" from multiple files "ifiles", and load it into a matrix
            where each row represents a new model (ifile) and each column represents the one dimension
            of the variable being loaded. varname must have the same len in all ifiles. Optionally specify a
            time-mean, e.g. tmean='yearmean', which will result in appropriately mean values being caculated 
            via cdo and returned.
            
            Requires netCDF4, cdo bindings and numpy 
            Returns a masked numpy array, varmat.
        """
        # Determine the dimensions of the matrix.
        def loadvar( ifile, varname, tmean ):
	      if ( tmean ):
		  cdo_call = 'cdo.' + tmean + '(input=ifile, returnMaArray=varname ).squeeze()'
                  var = eval( cdo_call )
	      else:	
	          nc = Dataset( ifile , 'r' )
	          var = nc.variables[ varname ][:].squeeze()
	      return var
	      
        vst = loadvar( ifiles[0], varname, tmean )
        varmat = np.ones( ( len(ifiles), len(vst) ) )*999e99
        
        for k, ifile in enumerate( ifiles ):
	    print ifile
	    varmat[k,:] = loadvar( ifile, varname, tmean )

        varmat = np.ma.masked_equal( varmat, 999e99 )
        return varmat
         

