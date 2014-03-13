import cdo as cdo; cdo = cdo.Cdo() # recommended import
import os
from numpy import squeeze

os.system( 'rm -rf /tmp/cdo*') # clean out tmp to make space for CDO processing.

def loadvar( ifile , varname, remap='', start_date='', end_date='', timmean=False):
        """  
            Load a CMIP5 netcdf variable "varname" from "ifile" and optionally 1) distance
            weighted remap to a given grid (e.g. 'r360x180), 2) select a date range between 
            start_date and end_date (format: 'YYYY-MM-DD') and 3) time-mean over the whole 
            record, or between the selected dates. Requires netCDF4, CDO and CDO python bindings.
            Returns a masked array, var.
        """

        date_range = start_date + ',' + end_date

        if ( timmean == True ) and ( start_date ) and ( remap ) :
            in_str = "-timmean -seldate," + date_range + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )

        elif ( timmean == True ) and ( remap ) :
            in_str = "-timmean" + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )

        elif ( start_date ) and ( remap ) :
            in_str = "-seldate," + date_range + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )

        elif  ( timmean == True ) and ( start_date ):
            var = cdo.timmean( input = cdo.seldate( date_range, input=ifile ), 
                               returnMaArray=varname )

        elif ( remap ) :
            var = cdo.remapdis( remap , input = ifile, returnMaArray=varname )

        elif ( timmean == True ):
            var = cdo.timmean( input=ifile, returnMaArray=varname ) 

        elif ( start_date ):
            var = cdo.seldate( date_range, input=ifile, returnMaArray=varname )

        else :
            from netCDF4 import Dataset
            nc = Dataset( ifile , 'r' )
            var = nc.variables[ varname ]

        return squeeze( var )
         

