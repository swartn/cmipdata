"""preprocessing_tools
======================

The preprocessing_tools module of cmipdata is a set of functions which use 
os.system calls to cdo to systematically apply a given processing on multiple 
NetCDF files, which listed in cmipdata ensemble objects. Methods:

Multi-file operators (cannot be chained):
 - cat_exp_slices 
 - cat_experiments
 - ens_stats
 
File-by-file operators (can be chained):
 - area_intgral*
 - area_mean
 - climatology
 - zonal_integral*
 - zonal_mean
 - remap
 - time_slice
 
 * to come
 
Neil Swart, 07/2014
"""
import os
import glob
from cd_classes import Ensemble, Model, Experiment, Realization, Variable
import copy
import itertools

#=======================================================================================================
# The next three operators work on multiple files across the ensemble, and cannot be chained together.
#=======================================================================================================

def cat_exp_slices(ens, delete=True):
    """
    For models which divide their output into multiple files per experiment (time-slices), cat_exp_slices concatenates
    the files into one unified file using CDO, and deletes the individual slices, unless delete=False. As input 
    cat_exp_slices takes a cmipdata ensemble object (see mkensemble). Unified experiment files are written to the 
    current working directory, and an updated ensemble object is returned
    
    The input ensemble can contain multiple models, experiments, realizations and variables, which cat_exp_slices 
    will process independently. In other words, files are joined per-model, per-experiment, per-relization, per-variable.
    For example, if the ensemble contains two experiments for many models/realizations for variable psl, two unified
    files will be produced per realization: one for the historical and one for the rcp45 experiment. To join files
    over experiments (e.g. to concatenate historical and rcp45) see cat_experiments.  
    
    EXAMPLE:
    
    # For a simple ensemble comprized of only 1 model, 1 experiment and one realization. 
    
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

     #=======================
     # Do the concantenation
     #=======================
     ens = cd.cat_exp_slices(ens)         

    # Look at the ensemble structure before the concatenation
    ens.fulldetails()
    HadCM3:
        historical
                r1i1p1
                        ts
                                ts_Amon_HadCM3_historical_r1i1p1_185912-200512.nc
                               
    """ 
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
		        
		        catstring = 'cdo cat ' + infiles + ' ' + outfile			
		        
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
    """ For variable (named variable_name) concatenate experiments exp1 and exp2 
    into a single file for each realization of each model listed in ensemble ens, and 
    return an updated ensemble object.
    
    - ens is a cmipdata ensemble object (see mkensemble).
    - variable_name is a string corresponding to a variable in ens.
    - exp1 and exp2 are strings defining the two experiments to be concatenated 
      (e.g. exp1='historical', exp2='rcp45').
      
    For each realization, the concatenated file for variable variable_name is written 
    to the current working directory and the input files are deleted by default, 
    unless delete=False.
    
    The concatenation occurs for each realization for which input files
    exist for both exp1 and exp2.  If no match is found for the realization 
    in exp1 (i.e. there is no corresponding realization in exp2), then the files 
    for both experiments are deleted from the path (unless delete=False) and 
    the realization is removed from ens. Similarly if exp2 is missing for a 
    given model, that model is deleted from ens.     
    """
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
		
		# Check if the end of e1 and the beggining of e2 seem to line up
		# if not, attempt to limit the e1 file endpoint
		if max(e1v.end_dates) > min(e2v.start_dates):
		    print '\n WARNING: %s end date is after %s start date for %s %s, attempting correction with cdo... \n' \
		    % (e1.name, e2.name, model.name, e1r.name)
		    
		    e1_start_year = int( min(e1v.start_dates)/100 ) # Experiment 2 starts on this year: get year assuming YYYYMM format      			     
		    e2_start_year = int( min(e2v.start_dates)/100 ) # Experiment 2 starts on this year: get year assuming YYYYMM format      
		    e1_end_year = e2_start_year - 1                 # Experiment 1 should end 1 year before
		    
		    
		    # First concatenate all experiment 1 files, if there is more than one
		    if len(e1v.filenames) > 1:
		        procfile = e1v.name + '_' + e1v.realm + '_'+ model.name + '_' + e1.name \
		                           + '_' + e1r.name + '_' + str(min(e1v.start_dates) ) + '-' + str(max(e1v.end_dates) ) + '.nc'
		    
		        catstring = 'cdo cat ' + ' '.join(e1v.filenames) + ' ' + procfile
		        ex = os.system( catstring )
		    else:
			procfile = ' '.join(e1v.filenames)
		    
		    """If the initial join of e1 files worked, time-slice the result with an appropriate end-date"""
		    outfile = e1v.name + '_' + e1v.realm + '_'+ model.name + '_' + e1.name \
		                             + '_' + e1r.name + '_' + str(min(e1v.start_dates) ) + '-' + str(e1_end_year) + '12' + '.nc'
		    
		    catstring = 'cdo -seldate,' + str(e1_start_year) + '-01-01' + ',' + str(e1_end_year) + '-12-31' + ' ' + procfile + ' ' + outfile	    
		    ex = os.system( catstring )
		        
  		    if ex == 0:
			"""If the fix was sucessfull, add the new file name to ens"""
		        e1v.filenames = [outfile]
		        print '\n %s end date is now %s12 and %s start date is %s01 \n' % (e1.name, e1_end_year, e2.name, e2_start_year)  
		    
		        # Add the newly created processing files to the delete list
		        del_ens.get_model(model.name).get_experiment(e1.name).get_realization(e1r.name).get_variable(e1v.name).add_filename(outfile)
		        del_ens.get_model(model.name).get_experiment(e1.name).get_realization(e1r.name).get_variable(e1v.name).add_filename(procfile)
		        
		    else:
			"""print warning and delete the realization from the two experiments in ens"""
			print '\n fix failed, deleting realization \n'.upper()
			e1.del_realization(e1r)
			e2.del_realization(e2r)
		        if realization_misses:
			    """Add to the list if it exists"""
		            realizations_to_delete[model.name] = list(realization_misses) + e1r.name
		        else:
		            realizations_to_delete[model.name] = [e1r.name]

			continue # if this failed to fix the problem, return to the top of the realization for loop.
			
			      
		# join the two experiments original filenames with a whitespace      
		infiles = ' '.join( e1v.filenames + e2v.filenames )
		
		# construct the output filename
		outfile = e1v.name + '_' + e1v.realm + '_'+ model.name + '_' + e1.name + '-' + e2.name +\
		'_' + e1r.name + '_' + str(min(e1v.start_dates) ) + '-' + str( max(e2v.end_dates) ) + '.nc'
		
		# do the concatenation using CDO
		print "\n joining " + model.name + '_' + e1r.name + ' ' + e1.name + ' to ' + e2.name  
		catstring = 'cdo cat ' + infiles + ' ' + outfile			    
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
    """ Calculate the ensemble mean and standard deviation over all models-realizations 
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
# (in principle, not implemented).
#============================================================================================
    
     
def areaint():
    print "hello this is areaint"
    
def areamean(ens, delete=True):
    """
    For each file in ens, calculate the area mean using CDO fldmean, 
    and do a smart naming of the output and remove the input files 
    if delete=True. An updated ensemble object is also returned.
    
    EXAMPLE:
    
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
    For each file in ens, calculate the zonal mean using CDO zonmean, 
    and do a smart naming of the output and remove the input files 
    if delete=True (default). An updated ensemble object is also returned.
    
    EXAMPLE:
    
    zonal_mean_ens = cd.zonmean(ens)
    
    """ 
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = ' zonal-mean_' + infile

            cdo_str = 'cdo zonmean ' + infile + ' ' + outfile 			
            os.system( cdo_str )

            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	        
	    variable.del_filename(infile)
	    variable.add_filename(outfile)
	    
    return ens	
  

def climatology(ens, delete=True):
    """
    For each file in ens, calculate the monthly climatology over the full file-length 
    using CDO ymonmean, and do a smart naming of the output and remove the input files 
    if delete=True (default). An updated ensemble object is also returned.
    
    If you want to compute the climatology over a specific time slice, use time_slice
    before compute the climatology.
    
    EXAMPLE:
    
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
    For each file in ens, remap to resolution remap='r_nlon_x_nlat_', where _nlon_, _nlat_ are the 
    number of lat-lon points to use. The remap is done using cdo and a smart naming of the output and 
    removal of the input files occurs if delete=True (default). An updated ensemble object is also returned.
    
    By default the distance weighted remapping is used, but any valid cdo remapping method can be used
    by specifying the option argument 'method', e.g. method='remapdis'.
    
    EXAMPLE:
       
    """ 
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = ' remap_' + infile

            cdo_str = 'cdo ' + method + ',' + remap + ' -selvar,' + variable.name + ' ' + infile + ' ' + outfile 			
            os.system( cdo_str )

            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	        
	    variable.del_filename(infile)
	    variable.add_filename(outfile)
	    
    return ens	



def time_slice(ens, start_date, end_date, delete=True):
    """
    For each file in ens, limit the date range to between start_date and end_date, 
    do a smart naming of the output and remove the input files 
    if delete=True. An updated ensemble object is also returned.
    
    start_date and end_date format is YYYY-MM-DD
    
    """ 
    date_range = start_date + ',' + end_date
    
    start_yyymm = start_date.replace('-','')[0:6] # convert dates to CMIP YYYYMM format
    end_yyymm   = end_date.replace('-','')[0:6]   
    
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:

            
            if ( min(variable.start_dates) != int(start_yyymm) ) and ( max(variable.end_dates) != int(end_yyymm) ):
		# Only yf the file doesnlt already have the correct date-range		
		if ( min(variable.start_dates) <= int(start_yyymm) ) and ( max(variable.end_dates) >= int(end_yyymm) ):
		    # Do the time-slicing if the file is within the specified dates
		    outfile =  variable.name + '_' + variable.realm + '_'+ model.name + '_' + experiment.name +\
		    '_' + realization.name + '_' + start_yyymm \
		    + '-' + end_yyymm + '.nc'
		    
		    cdo_str = 'cdo seldate,' + date_range + '  -selvar,' + variable.name + ' ' + infile +  ' ' + outfile           
		    os.system( cdo_str )
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
	        
    ens = ens.squeeze()	            	    
    return ens	          

def time_anomaly(ens, start_date, end_date, delete=False):
    """
    For each file in ens, compute the anomaly relative the period 
    between start_date and end_date, do a smart naming of the output 
    and remove the input files if delete=True. An updated ensemble 
    object is also returned.
    
    start_date and end_date format is YYYY-MM-DD
    
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
    For each file in ens, apply the cdo command contained in
    my_cdo_str, creating an output file appended by 'output_prefix'
    which is 'processed_' by default. An updated ensemble object
    is returned.
    
    Optionally delete the original input files if delete=True.
    
    EXAMPLE:
    
    my_ens = cd.my_operator(ens, 'cdo -yearmean', output_prefix='annual_')
    
    FUTURE EXPANSION:
    can easily handle more complex cases by passing a dict to my_cdo_str
    and mapping defined variables such as infile...
    
    defined variables are:
    model, experiment, realization, variable, infile, outfile
    
    e.g. my_cdo_str = 'cdo sub {infile} -timmean -seldate,1991-01-01,2000-12-31 {infile} {outfile}'
    
    and in the function:
        for model, experiment, realization, variable, files in ens.iterate():
            for infile in files:
               my_cdo_str.format(infile='file_input.nc',outfile='file_output.nc')

    """ 
    for model, experiment, realization, variable, files in ens.iterate():
        for infile in files:
            outfile = output_prefix + infile
            cdo_str=''
            values = {'model':model,'experiment':experiment,'realization':realization \
                      , 'variable':variable, 'infile':infile, 'outfile':outfile}

           
            cdo_str = my_cdo_str.format(**values)
            ex = os.system( cdo_str )
	    
	    if ex == 0:
		""" Add the filename for the newly processed file, if
		processing was sucessfull"""
	        variable.add_filename(outfile)
            
	    variable.del_filename(infile) # remove original filename from the ensemble.
            
            if delete == True:
                delstr = 'rm ' + infile
	        os.system( delstr )    
	        
    ens  = ens.squeeze()	        	    
    return ens	        
        
        
        
        
        
        
        
        
        
        
        