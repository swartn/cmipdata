import os
import glob
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

def cat_experiments(ens, exp1, exp2, delete_exps=True, delete_missing=True):
    """ Concatenate experiments exp1 and exp2 in ens into a single file.
    ens is a cmipdata ensemble object (see mkensemble) and exp1 and exp2
    are strings defining the two experiments to be concatenated 
    (e.g. exp1='historical', exp2='rcp45').
    
    The concatenated file is written to the current working directory
    and the two input files are deleted by default, unless delete_exp=False.
    
    The concatenation occurs for each realization for which input files
    exist for both exp1 and exp2. If the ensemble contains multiple 
    variables, the concatenation is done on each variables files. If no
    match is found for the realization in exp1 (i.e. there is no corresponding 
    realization in exp2), then the files for both experiments are deleted from
    the path unless delete_missing=False. 
    
    By default, with delete_exp=True and delete_missing=True, the only files which 
    will be left are those representing the concatenated experiments.   
    """
    for model in ens.models:
        experiment1 = model.get_experiment(exp1)
        experiment2 = model.get_experiment(exp2)

        if (experiment1 != [] ) and (experiment2 !=[]):
  	    for realization_e1 in experiment1.realizations:
		
	        realization_e2 = experiment2.get_realization(realization_e1.name)  
	        for variable_e1 in realization_e1.variables:
   	            if realization_e2 != []:
		        variable_e2 = realization_e2.get_variable(variable_e1.name)
		        if variable_e2 != []:
            	            modfiles = variable_e1.filenames + variable_e2.filenames

		            print "\n joining... " + model.name + ' ' + realization_e1.name + ' ' + variable_e1.name + ' : ' + experiment1.name + ' to ' + experiment2.name 
                            infiles = ' '.join( modfiles )
                            outfile = variable_e1.name + '_' + variable_e1.realm + '_'+ model.name + '_' + experiment1.name + '-' + experiment2.name + \
		            '_' + realization_e1.name + '_' + str(min(variable_e1.start_dates) ) + '-' + str( max(variable_e2.end_dates) ) + '.nc'
		            catstring = 'cdo cat ' + infiles + ' ' + outfile			
		            os.system( catstring )
		        
		            # delete the experiment files from the directory
		            if delete_exps == True:
		                for cfile in modfiles:
		                    delstr = 'rm ' + cfile
		                    os.system( delstr )     

		        # if there is not a matching variable in experiment 2, delete the experiment 1 files
		        # for that variable, as long as delete_missing=True.
                        else:
		            if delete_missing == True:
		                for cfile in variable_e1.filenames:
		                    delstr = 'rm ' + cfile
		                    os.system( delstr ) 
		                
                    # if there is not a matching realization in experiment 2, delete the experiment 1 files
	            # for all variables as long as delete_missing=True.		                
	            else:		
		        if delete_missing == True:
		            for cfile in variable_e1.filenames:
		                delstr = 'rm ' + cfile
		                os.system( delstr ) 
	
	# If experiment2 is missing, delete all the experiment 1 files
	elif experiment2 == [] :     
	    print 'model %s missing experiment %s, deleting' % (model.name, exp2)
      	    for realization_e1 in experiment1.realizations:
		for variable_e1 in realization_e1.variables:
	            if delete_missing == True:
		        for cfile in variable_e1.filenames:
		            delstr = 'rm ' + cfile
		            os.system( delstr ) 
		            
	# If experiment1 is missing, delete all the experiment2 files
	elif experiment1 == [] :     
	    print 'model %s missing experiment %s, deleting' % (model.name, exp1)
      	    for realization_e2 in experiment2.realizations:
		for variable_e2 in realization_e2.variables:
	            if delete_missing == True:
		        for cfile in variable_e2.filenames:
		            delstr = 'rm ' + cfile
		            os.system( delstr ) 	

    ens2 = mkensemble(variable_e1.name + '_' + variable_e1.realm + '*' + experiment1.name + '-' + experiment2.name + '*.nc')		            
    return ens2	        	        