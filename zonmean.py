import os
import glob

def zonmean(filenames, remap='', delete=False):
    """
    Zonal mean each file in filenames using CDO, and do a smart naming of the output and remove the mess (input files) if delete=True. Optionally remapdis to a given grid, (e.g. remap='r360x180') before taking the mean.
    """ 

    for cfile in filenames:
        print 'zonal mean of: ', cfile
        infile = cfile
        outfile = ' xm_' + cfile

        if ( remap ):
            catstring = 'cdo zonmean -remapdis,' + remap + ' ' + infile + outfile 			
        else:
            catstring = 'cdo zonmean ' + infile + outfile 			
  
        os.system( catstring )

        if delete == True:
            delstr = 'rm ' + cfile
	    os.system( delstr )
 
