import os
import glob
def remap_cmip_nc( filenames, remap='r360x180', start_date='' , end_date='', delete=False):
    """ Do a remap using CDO of multiple CMIP type nc files, given in filenames, and do a smart naming of the output (give the correct year-range in the output file name) and remove the mess (input files). Optionally allow the selection of a start_date and end_date to time-limit the file before remapping.
    """ 
    for cfile in filenames:
        print cfile
        varname = cfile.split('_')[0]
        mod = cfile.split( '_' )[2] 
        realm = cfile.split('_')[1]
        ensmember = cfile.split('_')[4]
        exp = cfile.split('_')[3]

        print mod

        if ( start_date ) and ( remap ) :
            print 'cmipdata.remap: remap and time limit'
            remapstr = 'cdo -remapdis,' + remap + ' -selvar,' + varname + ' -seldate,' + start_date + ',' + end_date + ' ' + cfile + ' ' +\
             'rm_' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + start_date.replace('-','')[0:6] + '-' +\
              end_date.replace('-','')[0:6] + '.nc' 
        else:
            print 'cmipdata.remap: remap only'
            start_datep = cfile.split('_')[5].split('-')[0]
            end_datep = cfile.split('_')[5].split('-')[1]
            remapstr = 'cdo -remapdis,' + remap + ' -selvar,' + varname + ' ' + cfile + ' ' +\
             'rm_' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + start_datep + '-' +\
              end_datep + '.nc' 

        print
        os.system( remapstr )

        if delete == True:
            delstr = 'rm ' + cfile
            os.system( delstr )



