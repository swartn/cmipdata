import os
import glob
from cd_classes import Ensemble, Model, Experiment, Realization, Variable
import copy
#from cmipdata import cmipdata

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
		    
		    
		    # Concatenate all experiment 1 files, and time limit them to the correct end-year
		    outfile = e1v.name + '_' + e1v.realm + '_'+ model.name + '_' + e1.name \
		    + '_' + e1r.name + '_' + str(min(e1v.start_dates) ) + '-' + str(e1_end_year) + '-12-31' + '.nc'
		    catstring = 'cdo -seldate,' + str(e1_start_year) + '-01-01' + ',' + str(e1_end_year) + '-12-31' + ' -cat ' + ' '.join(e1v.filenames) + ' ' + outfile
		    os.system( catstring )
		    e1v.filenames = [outfile]
		    print '%s end date is now %s12 and %s start date is %s01 \n' % (e1.name, e1_end_year, e2.name, e2_start_year)  
			      
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
		v.add_filename(outfile)
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
    
    return ens		

# Not working below here.    
     
def areaint():
    print "hello this is areaint"
    
    

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




        
        
        
        
        
        
        
        
        
        
        
        
        
        