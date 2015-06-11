"""preprocessing_tools
======================
 The preprocessing_tools module of cmipdata is a set of functions which use 
 os.system calls to Climate Data Operators (cdo) to systematically apply a 
 given processing on multiple NetCDF files, which are listed in cmipdata 
 ensemble objects.

  .. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>
"""
import os
import glob
from classes import Ensemble, Model, Experiment, Realization, Variable
import copy
import itertools

#===========================================================================
# The next three operators work on multiple files across the ensemble, 
# and cannot be chained together.
#=============================================================================

def cat_exp_slices(ens, delete=True):
    """
    Concatenate multiple time-slice files per experiment.
    
    For all models in ens which divide their output into multiple files per 
    experiment (time-slices), cat_exp_slices concatenates the files into one 
    unified file, and deletes the individual slices, unless delete=False. 
    The input ensemble can contain multiple models, experiments, realizations 
    and variables, which cat_exp_slices will process independently. In other words, 
    files are joined per-model, per-experiment, per-relization, per-variable.
    For example, if the ensemble contains two experiments for many models/realizations 
    for variable psl, two unified files will be produced per realization: one for the 
    historical and one for the rcp45 experiment. To join files
    over experiments (e.g. to concatenate historical and rcp45) see cat_experiments.  

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the concatenation.
    delete : boolean
             If delete=True, delete the individual time-slice files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          concatenated files.
    
    The concatenated files are written to present working directory.
    
    See also
    --------
    cat_experiments : Concatenate the files for two experiments.
    
    Examples
    ---------
    For a simple ensemble comprized of only 1 model, 1 experiment and one realization.::    
    
      # Look at the ensemble structure before the concatenation
      ens.fulldetails()
      HadCM3:
          historical
                  r1i1p1
                          ts
                                ts_Amon_HadCM3_historical_r1i1p1_185912-188411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_188412-190911.nc
                                ts_Amon_HadCM3_historical_r1i1p1_190912-193411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_193412-195911.nc
                                ts_Amon_HadCM3_historical_r1i1p1_195912-198411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_198412-200512.nc

      # Do the concantenation
      ens = cd.cat_exp_slices(ens)         

      # Look at the ensemble structure before the concatenation
      ens.fulldetails()
      HadCM3:
          historical
                  r1i1p1
                          ts
                                ts_Amon_HadCM3_historical_r1i1p1_185912-200512.nc
                               
    """ 
    # Set the env variable to skip repeated times
    os.environ["SKIP_SAME_TIME"] = "1" 
    
    # Loop over all models, experiments, realizations and variables
    for model in ens.models:
        for experiment in model.experiments:
	    for realization in experiment.realizations:
		for variable in realization.variables:
		    modfiles = variable.filenames
       
                    # if there are multiple files (time-slices) concatenate them
	            if len( modfiles ) > 1:
		        print "\n joining... " + model.name + ' ' + experiment.name + ' ' + realization.name
		        
                        infiles = ' '.join( modfiles )
                        
                        outfile = variable.name + '_' + variable.realm + '_'+ model.name + '_' + experiment.name +\
		        '_' + realization.name + '_' + str(min(variable.start_dates) ) + '-' + str( max(variable.end_dates) ) + '.nc'
		        
		        catstring = 'cdo mergetime ' + infiles + ' ' + outfile	
		
		        
		        os.system( catstring )
		            
		        # update the filenames in the variable object    
		        variable.filenames = []
		        variable.add_filename(outfile)
		        
		        # delete the individual slices from the directory
		        if delete == True:
		            for cfile in modfiles:
		                delstr = 'rm ' + cfile
		                os.system( delstr ) 
    return ens		        

def cat_experiments(ens, variable_name, exp1_name, exp2_name, delete=True):
    """Concatenate the files for two experiments. 
    
    Experiments exp1 and exp2 are concatenated into a single file for each 
    realization of each model listed in ens. For each realization, the concatenated file 
    for variable variable_name is written to the current working directory and the input files 
    are deleted by default, unless delete=False.
    
    The concatenation occurs for each realization for which input files
    exist for both exp1 and exp2.  If no match is found for the realization 
    in exp1 (i.e. there is no corresponding realization in exp2), then the files 
    for both experiments are deleted from the path (unless delete=False) and 
    the realization is removed from ens. Similarly if exp2 is missing for a 
    given model, that model is deleted from ens.  
       
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the concatenation.
          
    variable_name : str
                    The name of the variable to be concatenated.
                    
    exp1_name : str
                    The name of the first experiment to be concatenated (e.g. 'historical'). 
                    
    exp2_name : str
                    The name of the second experiment to be concatenated (e.g. 'rcp45').                     
            
    delete : boolean
             If delete=True, delete the individual time-slice files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          concatenated files.
    
          The concatenated files are written to present working directory.
    
    Examples
    ---------
    
    1. Join the historical and rcp45 simulations for variable ts in ens::
    
        ens = cd.cat_experiments(ens, 'ts', exp1_name='historical', exp2_name='rcp45')
 
    """
    # Set the env variable to skip repeated times
    os.environ["SKIP_SAME_TIME"] = "1" 
    
    # Create a copy of ens to use later for deleting input files if delete=True
    del_ens = copy.deepcopy(ens)

    # a list of models to remove from ens, if one experiment is missing completely from the model
    models_to_delete = {}
    # a list of realizations to remove from ens, if the realization is missing from one experiment
    realizations_to_delete = {}
    
    # Loop over all models
    for model in ens.models:
        e1 = model.get_experiment(exp1_name)
        e2 = model.get_experiment(exp2_name)

        # if the model is missing one experiment, remove that model from ens.
        if (e1 != []) and (e2 != []):
	    # Get a list of realizations names in the two experiments.
	    e1_r_names = [ r.name for r in e1.realizations ]
	    e2_r_names = [ r.name for r in e2.realizations ]
	    
	    # Find matching realizations btwn the two experiments.
	    realization_matches = set( e1_r_names ).intersection( e2_r_names )
            realization_misses = set( e1_r_names ).difference( e2_r_names )
            
            # add non-matching realizations to the realizations_deleted dict for printing later
	    if realization_misses:
		realizations_to_delete[model.name] = realization_misses
	    
	    # Delete non-matching realizations from ens, and do the join for matching ones.
	    for realization_name in realization_matches:
		# Get the realizations
		e1r = e1.get_realization(realization_name)
		e2r = e2.get_realization(realization_name)
		
		# Get the variable objects from the two experiments
		e1v = e1r.get_variable(variable_name)
		e2v = e2r.get_variable(variable_name)
		
		# join the two experiments original filenames with a whitespace    
		infiles = ' '.join( e1v.filenames + e2v.filenames )
		
		# construct the output filename
		outfile = e1v.name + '_' + e1v.realm + '_'+ model.name + '_' + e1.name + '-' + e2.name +\
		'_' + e1r.name + '_' + str(min(e1v.start_dates) ) + '-' + str( max(e2v.end_dates) ) + '.nc'
		
		# do the concatenation using CDO
		print "\n joining " + model.name + '_' + e1r.name + ' ' + e1.name + ' to ' + e2.name  
		catstring = 'cdo mergetime ' + infiles + ' ' + outfile		
	    
		os.system( catstring )
		
		# Add a new joined experiment to ens, 
		# with a newly minted realization, variable + filenames.
		v = Variable(e1v.name)
		v.add_realm(e1v.realm)	
		v.add_filename(outfile)
		v.add_start_date(min(e1v.start_dates))
	        v.add_end_date(max(e2v.end_dates))
		r = Realization(e1r.name)
		r.add_variable(v)
		joined_e = Experiment( e1.name + '-' + e2.name )
		joined_e.add_realization(r)
		model.add_experiment(joined_e)
		    
            # delete e1 and e2, which have been replaced with joined_e
            model.del_experiment(e1)
            model.del_experiment(e2)
            
        elif (e1 != []):
            models_to_delete[model.name] = e1.name
        elif (e2 != []):
            models_to_delete[model.name] = e2.name
            
    # If delete=True, delete the original files for variable_name, 
    # leaving only the newly joined ones behind. 		    
    if delete == True:		    
        for model in del_ens.models:
	    for experiment in model.experiments:
		for realization in experiment.realizations:
		    variable = realization.get_variable(variable_name)
		    for cfile in variable.filenames:
		        delstr = 'rm ' + cfile
		        os.system( delstr ) 
		        
    # Remove models with missing experiments from ens, and then return ens
    print ' \n\n Models deleted from ensemble (missing one experiment completely): \n'
    print '\t Model \t Experiment \n'
    
    for model_name, missing_experiment in models_to_delete.iteritems():
        ens.del_model( ens.get_model(model_name) )
        print '\t %s \t %s' % (model_name, missing_experiment)

    print ' \n\n Realizations deleted (missing from one experiment): \n'
    print '\t Model \t Realizations \n'    
    for key, value in realizations_to_delete.iteritems():
	print '\t %s \t %s' % (key, ' '.join(value) )
    
    ens = ens.squeeze()
    return ens		

def ens_stats(ens, variable_name):
    """ Compute the ensemble mean and standard deviation.
    
    The ensemble mean and standard deviation is computed over all models-realizations 
    and experiments for variable variable_name in ens, such that each model has a weight 
    of one. An output file is written containing the ensemble mean and another file is 
    written with the standard deviation, containing the names '_ENS-MEAN_' and '_ENS-STD_'
    in the place of the model-name. If the ensemble contains multiple experiments, files
    are written for each experiment.
    
    The ensemble in ens must be homogenous. That is to say all files must be on the same
    grid and span the same time-frame, within each experiment (see remap, and time_slice for more).
    Additionally, variable_name should have only one filename per realization and experiment. That
    is, join_exp_slice should have been applied.
    
    The calculation is done by, first computing the mean over all realizations for each model; 
    then for the ensemble, calculating the mean over all models.
    
        Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the concatenation.
          
    variable_name : str
                    The name of the variable to be concatenated.
                    
    delete : boolean
             If delete=True, delete the individual time-slice files.
	            
    Returns 
    ------- 
    The ENS-MEAN and ENS-STD files are written to present working directory.
    
    Examples
    ---------
    
    1. Compute the statistics for the ts variable::
    
        >>cd.ens_stats(ens, 'ts')

    """

    # figure out all the experiments in the ensemble 
    experiment_list = []
    for model in ens.models:
	for experiment in model.experiments:
	    experiment_list.append(experiment.name)
    
    experiment_list = set( experiment_list )

    # Do the ensemble mean for each experiment separately
    for experiment_name in experiment_list:
        # Keep a record of all files to mean for this experiment
        files_to_mean = []
         
        for model in ens.models:
            # loop over all models, checking if they contain experiment. 
            experiment = model.get_experiment(experiment_name)
            
            if experiment != [] :
		#If model has experiment, add its files to the mean.
                realizations = experiment.realizations
                
	        # Get all realization files for model and variable_name
	        modfilesall = [ realization.get_variable(variable_name).filenames 
	                        for realization in realizations ]
	        modfilesall = list( itertools.chain.from_iterable(modfilesall) )        
	        print modfilesall                
	        # get an example variable for naming 
	        variable = realizations[0].get_variable(variable_name)
	   
                # Check if there is more than one realization, if so, first mean these.
                if len( realizations ) > 1:
                    in_files = ' '.join( modfilesall )
                    out_file = variable.name + '_' + variable.realm + '_' + model.name + '_' + experiment.name \
                                      + '_R-MEAN_' + '_' + str(variable.start_dates[0]) + '-' + str(variable.end_dates[0]) + '.nc'
                                 
                    cdo_str = 'cdo ensmean ' + in_files + ' ' + out_file
 
                    # If the realization mean already exists don't redo
                    if os.path.isfile(out_file):
                        files_to_mean.append( out_file )
                    else:
                        os.system( cdo_str )
                        files_to_mean.append( out_file )
                else:
                    files_to_mean.append( modfilesall[0] )

        # For this experiment make the mean over all models and for models with multitple 
        # realizations, uses the mean of all these realizations.
        in_files = ' '.join( files_to_mean )
        
        out_file = 'ENS-MEAN_' + variable.name + '_' + variable.realm + '_' + experiment_name + '_' + str(variable.start_dates[0])\
                               + '-' + str(variable.end_dates[0]) + '.nc'
                                
        cdo_str = 'cdo ensmean ' + in_files + ' ' + out_file
        os.system( cdo_str )

        # Now do the standard deviation
        out_file = 'ENS-STD_' + variable.name + '_' + variable.realm + '_' + experiment_name + '_' + str(variable.start_dates[0])\
                              + '-' + str(variable.end_dates[0]) + '.nc'
                                
        cdo_str = 'cdo ensstd ' + in_files + ' ' + out_file
        os.system( cdo_str )    
    
#===========================================================================================
# The operators below this point work on a file-by-file basis and can be chained together 
# (in principle, not implemented). Practically my_operator can be used to chain operations.
#============================================================================================ 
     
def areaint(ens, delete=True):
    """
    Calculate the area weighted integral for each file in ens.
    
    The output files are prepended with 'area-integral'. The original 
    the input files are removed  if delete=True (default). An updated 
    ensemble object is also returned.
    
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.
          	 		 
    delete : boolean
             If delete=True, delete the original input files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          processed files.
    
    The processed files are also written to present working directory.
        
    Examples
    --------
    
    1. Compute the area integral for all files in ens::
    
        ens = cd.areaint(ens)
    
    """ 
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = ' area-integral_' + infile

            cdo_str = 'cdo fldsum -mul ' + infile + ' -gridarea ' + infile + outfile 			
            os.system( cdo_str )

            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	        
	    variable.del_filename(infile)
	    variable.add_filename(outfile)    
    
    return ens
    
    
def areamean(ens, delete=True):
    """
    Calculate the area mean for each file in ens.
    
    The output files are prepended with 'area-mean'. The original 
    the input files are removed  if delete=True (default). An updated 
    ensemble object is also returned.
    
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.
          	 		 
    delete : boolean
             If delete=True, delete the original input files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          processed files.
    
    The processed files are also written to present working directory.
        
    Examples
    --------
    
    1. Compute the area mean for all files in ens::
     
        area_mean_ens = cd.areamean(ens)
    
    """ 
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = ' area-mean_' + infile

            cdo_str = 'cdo fldmean ' + infile + outfile 			
            os.system( cdo_str )

            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	        
	    variable.del_filename(infile)
	    variable.add_filename(outfile)
	    
    return ens	    
        
def zonmean(ens, delete=True):
    """
    Calculate the zonal mean for each file in ens.
    
    The output files are prepended with 'zonal-mean'. The original 
    the input files are removed  if delete=True (default). An updated 
    ensemble object is also returned.
    
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.
          	 		 
    delete : boolean
             If delete=True, delete the original input files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          processed files.
    
    The processed files are also written to present working directory.
        
    Examples
    ---------
    
    1. Compute the zonal mean for all files in ens::
    
        zonal_mean_ens = cd.zonmean(ens)
    
    """ 
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = 'zonal-mean_' + infile

            cdo_str = 'cdo zonmean ' + infile + ' ' + outfile 			
            ex = os.system( cdo_str )
            if ex == 0:                
	        variable.add_filename(outfile)
	    else:
		try:
		    # if zonmean aborted part-way, 
		    # delete the uncompleted outfile.
       		    print 'deleting ' + outfile
		    os.system('rm -f ' + outfile )
		except:
		    pass

	    variable.del_filename(infile)
	        
            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	        
    ens.squeeze()	       
    return ens	
 
def climatology(ens, delete=True):
    """
    Compute the monthly climatology for each file in ens.
    
    The climatology is calculated over the full file-length using 
    cdo ymonmean, and the output files are prepended with 'climatology_'. 
    The original the input files are removed  if delete=True (default). 
    An updated ensemble object is also returned.
    
    If you want to compute the climatology over a specific time slice, use time_slice
    before compute the climatology.
    
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the remapping.
          	 		 
    delete : boolean
             If delete=True, delete the original input files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          processed files.
    
    The processed files are also written to present working directory.
        
    Examples
    --------
    
    1. Compute the climatology::
    
        climatology_ens = cd.climatology(ens)
    
    """ 
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = ' climatology_' + infile

            cdo_str = 'cdo ymonmean -selvar,' + variable.name +' ' + infile + ' ' + outfile 			
            os.system( cdo_str )

            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	        
	    variable.del_filename(infile)
	    variable.add_filename(outfile)
	    
    return ens	


def remap(ens, remap='r360x180', method='remapdis', delete=True):
    """
    Remap files to a specified resolution.
    
    For each file in ens, remap to resolution remap='r_nlon_x_nlat_', where _nlon_, 
    _nlat_ are the number of lat-lon points to use. Removal of the original input 
    files occurs if delete=True (default). An updated ensemble object is also returned.
    
    By default the distance weighted remapping is used, but any valid cdo 
    remapping method can be used by specifying the option argument 'method', 
    e.g. method='remapdis'.
    
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the remapping.
          
    remap : str
          The resolution to remap to, e.g. for a 1-degree grid remap='r360x180'
	 		 
    delete : boolean
             If delete=True, delete the original input files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          processed files.
    
    The processed files are also written to present working directory.
        
    
    EXAMPLE:
    --------
    
    1. remap files to a one-degree grid::
    
        ens = cd.remap(ens, remap='r1x180')
       
    """ 
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = 'remap_' + infile

            cdo_str = 'cdo ' + method + ',' + remap + ' -selvar,' + variable.name + ' ' + infile + ' ' + outfile 	
            print cdo_str
            ex = os.system( cdo_str )
            if ex == 0:
    	        variable.add_filename(outfile)

            variable.del_filename(infile)
                
            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	    
    return ens	


def time_slice(ens, start_date, end_date, delete=True):
    """
    Limit the data to the period between start_date and end_date,
    for each file in ens.
    
    The resulting output is written to file, named with with the correct 
    date range, and the original input files are deleted if delete=True.
    
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.
          
    start_date : str
                 Start date for the output file with format: YYYY-MM-DD
    end_date : str
                 End date for the output file with format: YYYY-MM-DD
	 		 
    delete : boolean
             If delete=True, delete the original input files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          processed files.
    
    The processed files are also written to present working directory.
        
    
    EXAMPLES
    ---------
    1. Select data between 1 January 1980 and 31 December 2013::
    
        ens = cd.time_slice(ens, start_date='1979-01-01', end_date='2013-12-31')

    """ 
    date_range = start_date + ',' + end_date
    
    start_yyymm = start_date.replace('-','')[0:6] # convert dates to CMIP YYYYMM format
    end_yyymm   = end_date.replace('-','')[0:6]   
    
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:           
            if ( min(variable.start_dates) != int(start_yyymm) ) or (max(variable.end_dates) != int(end_yyymm) ):
		# Only yf the file doesnlt already have the correct date-range		
		if ( min(variable.start_dates) <= int(start_yyymm) ) and ( max(variable.end_dates) >= int(end_yyymm) ):
		    # Do the time-slicing if the file is within the specified dates
		    outfile =  variable.name + '_' + variable.realm + '_'+ model.name + '_' + experiment.name +\
		    '_' + realization.name + '_' + start_yyymm \
		    + '-' + end_yyymm + '.nc'
		    
		    print 'time limiting...'
		    cdo_str = 'cdo seldate,' + date_range + '  -selvar,' + variable.name + ' ' + infile +  ' ' + outfile           
		    ex = os.system( cdo_str )
		    if ex == 0:
		        variable.add_filename(outfile)  # add the filename with new date-ranges to the variable in ens
		        variable.start_dates=[]; variable.end_dates=[]
		        variable.add_start_date(int(start_yyymm)) # add the start-date with new date-ranges to the variable in ens
		        variable.add_end_date(int(end_yyymm)) # add the end-date with new date-ranges to the variable in ens		    
		else:
		    #If the file does not containt he desired dates, print a warning and delete
	            print "%s %s is not in the date-range...deleting" %(model.name, realization.name)
	            
		variable.del_filename(infile) # delete the old filename from ens
   	       
                if delete == True:
                    delstr = 'rm ' + infile
	            os.system( delstr ) 
	        
    ens.squeeze()	            	    
    return ens	          

def time_anomaly(ens, start_date, end_date, delete=False):
    """
    Compute the anomaly relative the period between start_date and end_date,
    for each file in ens.
    
    The resulting output is written to file with the prefix 'anomaly_', and the 
    original input files are deleted if delete=True.
    
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.
          
    start_date : str
                 Start date for the base period with format: YYYY-MM-DD
    end_date : str
                 End date for the base period with format: YYYY-MM-DD
	 
		 
    delete : boolean
             If delete=True, delete the original input files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          processed files.
    
    The processed files are also written to present working directory.
        
    
    EXAMPLES
    ---------
    
    1. Compute the anomaly relative to the base period 1980 to 2010::
    
        ens = cd.time_anomaly(ens, start_date='1980-01-01', end_date='2010-12-31')
  
    """ 
    date_range = start_date + ',' + end_date
    
    start_yyymm = start_date.replace('-','')[0:6] # convert dates to CMIP YYYYMM format
    end_yyymm   = end_date.replace('-','')[0:6]   
    
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:

            # Do the time-slicing if the file is within the specified dates 
            if ( min(variable.start_dates) <= int(start_yyymm) ) and ( max(variable.end_dates) >= int(end_yyymm) ):
        
                outfile = 'anomaly_' + variable.name + '_' + variable.realm + '_'+ model.name + '_' + experiment.name +\
		                           '_' + realization.name + '_' +  str(variable.start_dates[0]) \
                                               + '-' + str(variable.end_dates[0]) + '.nc'
            
                cdo_str = 'cdo sub ' + infile +  ' -timmean -seldate,' + date_range + '  -selvar,' + variable.name + ' ' + infile +  ' ' + outfile           
                os.system( cdo_str )
	        variable.add_filename(outfile)  # add the filename with new date-ranges to the variable in ens

   	    variable.del_filename(infile) # delete the old filename from ens
   	       
            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	            	    
    return ens	
    
def my_operator(ens, my_cdo_str, output_prefix='processed_', delete=False):
    """
    Apply a customized cdo operation to all files in ens.
    
    For each file in ens the command in my_cdo_str is applied and an output 
    file appended by 'output_prefix' is created. 
    
    Optionally delete the original input files if delete=True.
    
    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.
          
    my_cdo_str : str
                 The (chain) of cdo commands to apply. Defined variables which can 
                 be used in my_cdo_str are: model, experiment, realization, variable, 
		 infile, outfile
		 
    output_prefix : str
                 The string to prepend to the processed filenames.		 
		 
    delete : boolean
             If delete=True, delete the original input files.
	            
    Returns 
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly 
          processed files.
    
    The processed files are also written to present working directory.
        
    
    EXAMPLES
    ---------

    1. Do an annual mean::
    
           my_cdo_str = 'cdo -yearmean {infile} {outfile}'
           my_ens = cd.my_operator(ens, my_cdo_str, output_prefix='annual_')
    
    2. Do a date selection and time mean::
    
           my_cdo_str = 'cdo sub {infile} -timmean -seldate,1991-01-01,2000-12-31 {infile} {outfile}'
           my_ens = cd.my_operator(ens, my_cdo_str, output_prefix='test_')
  
    """ 
    if delete == True:
	# Take a copy of the original ensemble before we modify it below
        del_ens = copy.deepcopy(ens)
    
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = output_prefix + infile
            cdo_str=''
            values = {'model':model,'experiment':experiment,'realization':realization \
                      , 'variable':variable, 'infile':infile, 'outfile':outfile}
          
            cdo_str = my_cdo_str.format(**values)
            ex = os.system( cdo_str )
	    
	    if ex == 0:
		#Add the filename for the newly processed file, if
		# processing was sucessfull
	        #variable.add_filename(outfile)
	        pass 
	    else:
		try:
		    # if processing aborted part-way, 
		    # delete the uncompleted outfile.
		    os.system('rm -f ' + outfile )
       		    print '\n Failed processing...deleting ' + outfile
		except:
		    pass	        
            
	    variable.del_filename(infile) # remove original filename from the ensemble.
            
    if delete == True:
        del_ens_files(del_ens)   
	        
    ens.squeeze()	        	    
    return ens	        
        
def del_ens_files(ens):
    """ delete from disk all files listed in ensemble ens"""
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
	        delstr = 'rm ' + infile
	        os.system( delstr ) 
	    
        
        
        
        
        
        
        
        
        
