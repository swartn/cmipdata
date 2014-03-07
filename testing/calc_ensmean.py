import glob
import os

def calc_ensmean():
    filenames = glob.glob("rm_*.nc")
    modelnames = [ filename.replace('rm_','').split( '_' )[2] for filename in filenames ]
    uniq_mods = set( modelnames )
    print
    print "--------------------"
    print "Number of models: " , len( uniq_mods )
    print "--------------------"
    print
    print " Name,        start, end,   # files: "
    
    files_to_mean = [] 

    for mod in uniq_mods:
       modmatch = 'rm_*_' + mod + '_*.nc'  
       modfilesall = glob.glob( modmatch )
       modfilesreg = [ modfile.replace('rm_','') for modfile in modfilesall ]
       allensmembers = [ modfile.split('_')[4] for modfile in modfilesreg ]
       uniq_ensmems = set( allensmembers )
 
       varname = modfilesreg[0].split('_')[0]
       realm = modfilesreg[0].split('_')[1]
       exp = modfilesreg[0].split('_')[3]
       start_date = modfilesreg[0].split( '_' )[5].split('-')[0] 
       end_date = modfilesreg[0].split( '_' )[5].split('-')[1].split('.')[0] 

       print mod, uniq_ensmems

       # Check if there is more than one realization, if so, first mean these.        
       if len( uniq_ensmems ) > 1:
           # mean over realizations
            in_files = ' '.join(  modfilesall )
            out_file =  varname + '_' + realm + '_' + mod + '_' + exp + '_R-MEAN_' + '_' + start_date.replace('-','')[0:6] + '-' +  end_date.replace('-','')[0:6] + '.nc'
            rm_str = 'cdo ensmean ' + in_files + ' ' + out_file
 
            # If the realization mean already exists don't redo
            if os.path.isfile(out_file): 
                files_to_mean.append( out_file )
            else:
                os.system( rm_str ) 
		files_to_mean.append( out_file )
       else:
            files_to_mean.append( modfilesall[0] )

    for cfile in files_to_mean:
        print cfile
        lstr = 'ncdump -h ' + cfile + ' | grep currently'				
        os.system(lstr)

    # make the mean over all models (and for models with multitple realizations, uses the mean of all these realizations).
    in_files = ' '.join( files_to_mean )
    out_file =  varname + '_' + realm + '_ENS-MEAN_' + exp + '_' + start_date.replace('-','')[0:6] + '-' +  end_date.replace('-','')[0:6] + '.nc'
    em_str = 'cdo ensmean ' + in_files + ' ' + out_file 
    #print em_str
    os.system( em_str ) 

    out_file_std =  varname + '_' + realm + '_ENS-STD_' + exp + '_' + start_date.replace('-','')[0:6] + '-' +  end_date.replace('-','')[0:6] + '.nc'
    estd_str = 'cdo ensstd ' + in_files + ' ' + out_file_std 
    #print em_str
    os.system( estd_str ) 


########################################################
calc_ensmean()
