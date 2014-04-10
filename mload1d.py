import os
import numpy as np 

def loadvar(ifiles, varname):
        """  
            Load a netcdf variable "varname" from multiple files "ifiles", and load it into a matrix
            where each row represents a new model (ifile) and each column represents the one dimension
            of the variable being loaded. varname must have the same len in all ifiles.
            
            Requires netCDF4 and numpy 
            Returns a masked numpy array, varmat.
        """
        # Determine the dimensions of the matrix.
        vst = loaddata( ifiles[0], varname )
        varmat = np.ones( len(ifiles), len(vst) )*999e99
        
        for k, ifile in enumerate( ifiles ):
	    varmat[k,:] = loaddata( ifile, varname )

        varmat = np.ma.masked_equal( varmat, 999e99 )
        return varmat
         

