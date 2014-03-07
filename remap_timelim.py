import os
import glob
def remap_cmip_nc( start_date , end_date ):
    """
    Do a remap of multiple CMIP type nc files given in filenames using CDO, and do a smart naming of the output (give the correct year-range in the output file name) and remove the mess (input files).
    """ 

    filenames = glob.glob("*.nc")
    modelnames = [ filename.split( '_' )[2] for filename in filenames ]
    uniq_mods = modelnames 
    print
    print "--------------------"
    print "Number of models: " , len( uniq_mods )
    print "--------------------"
    print

    for cfile in filenames:
        print cfile
        varname = cfile.split('_')[0]
        mod = cfile.split( '_' )[2] 
        realm = cfile.split('_')[1]
        ensmember = cfile.split('_')[4]
        exp = cfile.split('_')[3]

        print mod

        remapstr = 'cdo -remapdis,r360x180 -selvar,' + varname + ' -seldate,' + start_date + ',' + end_date + ' ' + cfile + ' ' + 'rm_' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + start_date.replace('-','')[0:6] + '-' +  end_date.replace('-','')[0:6] + '.nc' 
        
        os.system( remapstr )


remap_cmip_nc('1900-01-01', '2005-12-31' )
