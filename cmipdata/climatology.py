import os
import glob
def climatology( filenames, remap='', start_date='' , end_date='', delete=False):
    """ Create a monthly climatology from CMIP5 data using cdo. Optionaly also do a remap and allow the selection of a start_date and end_date to time-limit the file before remapping.
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
            print 'cmipdata.climatology: remap and time delimit before computing climatology'
            climstr = 'cdo ymonmean -remapdis,' + remap + ' -selvar,' + varname + ' -seldate,' + start_date + ',' + end_date + ' ' + cfile + ' ' +\
             'monclim_rm_' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + start_date.replace('-','')[0:6] + '-' +\
              end_date.replace('-','')[0:6] + '.nc' 

        elif (remap):
            print 'cmipdata.climatology: remap before computing climatology'
            start_datep = cfile.split('_')[5].split('-')[0]
            end_datep = cfile.split('_')[5].split('-')[1]
            climstr = 'cdo ymonmean -remapdis,' + remap + ' -selvar,' + varname + ' ' + cfile + ' ' +\
             'monclim_rm_' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + start_datep + '-' +\
              end_datep + '.nc'

        elif ( start_date ):
            print 'cmipdata.climatology: time delimit before computing climatology'
            climstr = 'cdo ymonmean -selvar,' + varname + ' -seldate,' + start_date + ',' + end_date + ' ' + cfile + ' ' +\
             'monclim_rm_' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + start_date.replace('-','')[0:6] + '-' +\
              end_date.replace('-','')[0:6] + '.nc'
 
        else:
            print 'cmipdata.climatology: Computing climatology (no remap or time-delimit)'
            start_datep = cfile.split('_')[5].split('-')[0]
            end_datep = cfile.split('_')[5].split('-')[1]
            climstr = 'cdo ymonmean -selvar,' + varname + ' ' + cfile + ' ' +\
             'monclim_rm_' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + start_datep + '-' +\
              end_datep + '.nc'


        print
        os.system( climstr )

        if delete == True:
            delstr = 'rm ' + cfile
            os.system( delstr )

