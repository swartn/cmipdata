import os
import glob

def zonmean(filenames, delete=False):
    """
    Zonal mean each file in filenames using CDO, and do a smart naming of the output and remove the mess (input files) if delete=True
    """ 

    for cfile in filenames:
        print 'zonal mean of: ', cfile
        infile = cfile
        outfile = ' xm_' + cfile
        catstring = 'cdo zonmean ' + infile + outfile 			
        os.system( catstring )

        if delete == True:
            delstr = 'rm ' + cfile
	    os.system( delstr )
 
