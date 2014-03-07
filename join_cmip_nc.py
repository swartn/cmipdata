import os
import glob
def join_cmip_nc():
    """
    Do a concatenation of multiple time-slice CMIP type nc files using CDO, and do a smart naming of the output (give the correct year-range in the output file name) and remove the mess (input files).
    """ 

    filenames = glob.glob("*.nc")
    modelnames = [ filename.split( '_' )[2] for filename in filenames ]
    uniq_mods = set( modelnames )
    print
    print "--------------------"
    print "Number of models: " , len( uniq_mods )
    print "--------------------"
    print
    print " Name,        start, end,   # files: "

    for mod in uniq_mods:
       modmatch = '*_' + mod + '_*.nc'
  
       modfilesall = glob.glob( modmatch )
       allensmembers = [ modfile.split('_')[4] for modfile in modfilesall ]
       uniq_ensmems = set( allensmembers )
       print mod, uniq_ensmems
       
       for ensmem in uniq_ensmems:
               modensmatch = '*_' + mod + '_*' + ensmem + '_*.nc'
               modfiles = glob.glob( modensmatch )
               print
               print 'files to cat for ' +  mod + ' :'
               print modfiles
               print 
	       start_dates = [ int( cfile.split( '_' )[5].split('-')[0]) \
		    for cfile in modfiles ]
	       end_dates = [ int( cfile.split( '_' )[5].split('-')[1].split('.')[0] )\
		    for cfile in modfiles ]

	       start_date = min( start_dates)
	       end_date = max( end_dates )

	       varname = modfiles[0].split('_')[0]
	       realm = modfiles[0].split('_')[1]
	       ensmember = modfiles[0].split('_')[4]
	       exp = modfiles[0].split('_')[3]

	       print mod, ensmem, start_date , end_date, len( modfiles)
	       print 
	       if len( modfiles ) > 1:
		  print "joining..."
		  catstring = 'cdo cat ' + modensmatch + ' ' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + str(start_date ) + '-' + str( end_date ) + '.nc'			
		  os.system( catstring )
		  for cfile in modfiles:
		      delstr = 'rm ' + cfile
		      os.system( delstr ) 

join_cmip_nc()
