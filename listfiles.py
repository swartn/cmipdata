import os
import glob

def listfiles( varname='*', experiment='*' ):
    """ (filenames, modelnames) = listfiles( varname, experiment ) 
    Create and return a list of all the inetcdf files in the current directory. If specified match only those files which begin with varname and are from the CMIP5 experiment "experiment".
    """
    match_string = varname  + '*' + experiment + '*.nc'
    filenames = sorted( glob.glob( match_string ) )

    modelnames = set( sorted( [filename.split( '_' )[2] for filename in filenames] ) )
    print
    print "--------------------"
    print "Number of models: " , len( modelnames )
    print "--------------------"

    return filenames, modelnames

