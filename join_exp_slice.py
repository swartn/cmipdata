import os
import glob

def join_exp_slice( filenames , modelnames ):
    """
    Do a concatenation of multiple time-slice CMIP type nc files using CDO, and do a smart naming of the output (give the correct year-range in the output file name) and remove the mess (input files). Use match_exp to make sure files exist for each realization if you are joining over two experiments.
    """ 

    for mod in modelnames:
       modfilesall = [ filename for filename in filenames if filename.split( '_' )[2] == mod ]
       ensmembersall = [ modfile.split('_')[4] for modfile in modfilesall ]
       uniq_ensmems = sorted( set( ensmembersall ) )
       
       for ensmem in uniq_ensmems:
               modfiles = [ modfilename for modfilename in modfilesall if 
                            modfilename.split( '_' )[4] == ensmem ]

	       start_dates = [ int( cfile.split( '_' )[5].split('-')[0]) 
		               for cfile in modfiles ]
	       end_dates = [ int( cfile.split( '_' )[5].split('-')[1].split('.')[0] )
		             for cfile in modfiles ]

	       start_date = min( start_dates)
	       end_date = max( end_dates )

	       varname = modfiles[0].split('_')[0]
	       realm = modfiles[0].split('_')[1]
	       ensmember = modfiles[0].split('_')[4]
	       exp = modfiles[0].split('_')[3]

	       print 
	       print mod, ensmem, start_date , end_date, len( modfiles)
	       if len( modfiles ) > 1:
		  print "joining... "
                  infiles = ' '.join( modfiles )
		  catstring = 'cdo cat ' + infiles + ' ' + varname + '_' + realm + '_'+ mod + '_' + exp + '_' + ensmember + '_' + str(start_date ) + '-' + str( end_date ) + '.nc'			
		  os.system( catstring )
		  for cfile in modfiles:
		      delstr = 'rm ' + cfile
		      os.system( delstr ) 


def match_exp( filenames , modelnames, rcpname='rcp45' ):
    """
    Description:
    For each model in modelnames, look through filenames and for each realization of the historical experiment check if
    that realization exists for the RCP experiment, rcpname. If files exist for both historical and rcp experiments,
    print out a message. If no match exists, delete all files for that realization. 
    
    Usage:
    For a directory with .nc files from many models, many realizations, and two or more experiments (e.g. historical and rcp45),
    you may want to keep only files for those models/realizations which have files for both experiments. For example, before
    running join_exp_slice, which would join all time-slice (and experiment) files for each model/realization, run match_exp.
    """

    for mod in modelnames:
       print "cmipdata.match_exp: Model ", mod 
       modfilesall = [ filename for filename in filenames if filename.split( '_' )[2] == mod ]

       modfiles_historical = [ filename for filename in modfilesall if filename.split( '_' )[3] == 'historical' ]
       ensmembers_hist = [ modfile.split('_')[4] for modfile in modfiles_historical ]
       uniq_ensmems_hist = sorted( set( ensmembers_hist ) )

       modfiles_rcp = [ filename for filename in modfilesall if filename.split( '_' )[3] == rcpname ]
       ensmembers_rcp = [ modfile.split('_')[4] for modfile in modfiles_rcp ]
       uniq_ensmems_rcp = sorted( set( ensmembers_rcp ) )

       for ensmem in uniq_ensmems_hist:
               modfiles = [ modfilename for modfilename in modfilesall if
                            modfilename.split( '_' )[4] == ensmem ]

               modfiles_historical_em = [ filename for filename in modfiles if filename.split( '_' )[3] == 'historical' ]

               if any( ensmem in s for s in uniq_ensmems_rcp):
                   print "Historical - RCP match for: ", ensmem
                   for cfile in modfiles_historical_em :
	               end_date =  int( cfile.split( '_' )[5].split('-')[1].split('.')[0] )
                       if end_date > 200512:
                           print "WARNINING: enddate is: ", end_date, "for ", mod, ensmem
                           print "time-limiting the file to end in 200512"
                           tlim_str = 'cdo -seldate,1850-01-01,2005-12-31 ' + cfile + ' tl_' + cfile
                           mv_str = 'mv tl_' + cfile + ' ' + cfile
                           print tlim_str
                           os.system(tlim_str)
                           os.system(mv_str) 
               else:
                   print " NO match for: ", ensmem, "...deleting"
                   for cfile in modfiles:
                       delstr = 'rm ' + cfile
                       os.system(delstr)
       print 
