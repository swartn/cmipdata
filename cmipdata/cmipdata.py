"""Defines the Ensemble, Model, Experiment, Realization and Variable objects of
cmipdata and associated functions.

Neil Swart, 22/07/2014
"""

import os
import glob

class Ensemble(object):
    """ Defines a cmipdata ensemble. The ensemble contains
    a list of model members.
    """
    def __init__(self):
        self.models = []    
        
    def __str__(self):
        return "Models in %s: \n %s" %(self.name, '\n'.join([m.name for m in self.models]))
        
    def num_models(self):
	""" Returns the number of models in the ensemble"""
        return len(self.models)

    def add_model(self, model):
	"""Adds the model object model to the ensemble"""
        self.models.append(model)
        
    def get_model(self, modelname):
        """Finds and returns the model object corresponding
	to modelname in the ensemble, or if no match is found, 
	returns an empty list.
	"""
	for model in self.models:
	    if model.name == modelname:
		m = model
		break
	else:
	    m = []
	return m
	
    def models(self):
	"""Retuns the list of model objects in the ensemble"""
        return self.models
        
class Model(object):
    """ Defines a model with a name.
    """
    def __init__(self, modelname):
        self.name = modelname
        self.experiments = []
               
    def add_experiment(self, experiment):
	"""Adds the experiment object experiment to the 
	models experiments
	"""
        self.experiments.append(experiment)

    def get_experiment(self, experimentname):
	"""Finds and returns the experiment object corresponding
	to experimnentname in the model experiment list, or if no 
	match is found, returns an empty list.
	"""
	for experiment in self.experiments:
	    if experiment.name == experimentname:
		e = experiment
		break
	else:
	    e = []
	return e    
    
    def experiments(self):
        return self.experiments 

class Experiment(object):
    """ Defines an experiment for a given model, with a name and a list of
    assiciated realizations, which can be retrieved with
    experiment.realizations(). New realizations can be added
    to the experiment with experiment.add_realization(realization)
    """
    def __init__(self, experimentname):
        self.name = experimentname
        self.realizations = []
        
    def __str__(self):
        return self.name
        
    def add_realization(self, realization):
	"""Adds the realization object experiment to the 
	experiments realizations.
	"""	
        self.realizations.append(realization)
        
    def get_realization(self, realizationname):
        """Finds and returns the realization object corresponding
	to realizationname in the experiment's realization list, or if no 
	match is found, returns an empty list.
	"""
	for realization in self.realizations:
	    if realization.name == realizationname:
		r = realization
		break
	else:
	    r = []
	return r            
        
    def realizations(self):
        return self.realizations        
                
class Realization(object):
    """ Defines a realization for a given model and experiment, 
    with a name and a list of
    assiciated variables, which can be retrieved with
    realization.variables(). New variables can be added
    to the realization with realization.add_variable(variable)
    """
    def __init__(self, realizationname):
        self.name = realizationname
        self.variables = []
        
    def add_variable(self, variable):
	"""Adds the variable object to the 
	realization's variables.
	"""	
        self.variables.append(variable)
        
    def get_variable(self, variablename):
        """Finds and returns the variable object corresponding
	to variablename in the realization's variable list, or if no 
	match is found, returns an empty list.
	"""	
	for variable in self.variables:
	    if variable.name == variablename:
		v = variable
		break
	else:
	    v = []
	return v
	
    def variables(self):
        return self.variables
        
class Variable(object):
    """Defines a variable for a given model, experiment and realization,
    with a name, and an associated list of filenames, which can be retrieved 
    with variable.filenames(). A new filename can be added with 
    variable.add_filename('filename.nc')
    """
    def __init__(self, variablename):
        self.name = variablename
        self.filenames = []
        
    def add_filename(self, filename):
	"""Adds filname to the variable's list of files"""
        self.filenames.append(filename)
        
    def filenames(self):
        """ Retuns a list of filenames associated with the variable"""	
        return self.filenames
        
   
def mkensemble(filepattern, experiment='*', prefix='', kwargs=''):
    """Creates and returns a cmipdata ensemble object from a list of 
    filenames matching filepattern. filepattern is a string that by default
    is matched against all files in the current directory. But filepattern 
    could include a full path to reference files not in the current directory, 
    and can also include wildcards. 
    
    Once the list of matching filenames is derived, the model, experiment,
    realization, variable, start_date and end_date fields are extracted by
    parsing the filnames against a specified file naming convention. By 
    default this is the CMIP5 convention, which is
    
    variable_realm_model_experiment_realization_startdate-enddate.nc
    
    Optionally specifying prefix will remove prefix from each filename
    before the parsing is done. This is useful, for example, to remove 
    pre-pended paths used in filepattern.
    
    EXAMPLES:
    
    # ensemble of all sea-level pressure files from the historical experiment in 
    # the current directory.
    
    ens = mkensemble('psl*historical*.nc') 
    
    # ensemble of all sea-level pressure files from all experiments in a non-local
    # directory
    
    ens = mkensemble('/home/ncs/ra40/cmip5/sam/c5_slp/psl*'
                      , prefix='/home/ncs/ra40/cmip5/sam/c5_slp/') 

    
    If the default CMIP5 naming convention is not used by your files,
    an arbitary naming convention for the parsing may be specified by
    kwargs. kwargs is a dictionary whos keys contain each element (model, 
    experiment,realization, variable, start_date and end_date) and
    whos values are the position in the filename that the element occurs.
    In addition, the key 'separator' must contain the element separator.
    For example, for the CMIP5 naming convention:
    
    kwargs = {'separator':'_', 'variable':0, 'realm':1, 'model':2, 'experiment':3,
    'realization':4, 'dates':5}
    
    ens = mkensemble('psl*.nc', **kwargs) 
    
    """
 
    # find all files matching filepattern
    filenames = sorted( glob.glob( filepattern ) )
   
    if kwargs == '':
        kwargs = {'separator':'_', 'variable':0, 'realm':1, 'model':2, 'experiment':3,
                  'realization':4, 'dates':5}

    # Initialize the ensemble object
    ens = Ensemble()
                  
    # Loop over all files and 
    for name in filenames:
	name = name.replace(prefix,'')
	variablename = name.split( kwargs['separator'] )[ kwargs['variable'] ]
	realm        = name.split( kwargs['separator'] )[ kwargs['realm'] ]
	modelname    = name.split( kwargs['separator'] )[ kwargs['model'] ]
	experiment   = name.split( kwargs['separator'] )[ kwargs['experiment'] ]
	realization  = name.split( kwargs['separator'] )[ kwargs['realization'] ]
	dates        = name.split( kwargs['separator'] )[ kwargs['dates'] ]
	start_date   = int( name.split( kwargs['separator'] )[5].split('-')[0]) 
	end_date     = int( name.split( kwargs['separator'] )[5].split('-')[1].split('.')[0] )
	
	# create the model if necessary
	m = ens.get_model(modelname)   
	if m == []:
	    m = Model(modelname)
	    ens.add_model(m)
	    # create the experiment if necessary    
	    e = m.get_experiment(experiment)   
	    if e == []:
		e = Experiment(experiment)
		m.add_experiment(e)
		#create the realization if necessary
		r = e.get_realization(realization)   
		if r == []:
		    r = Realization(realization)
		    e.add_realization(r)
		    # create the variable if necessary    
		    v = r.get_variable(variablename)   
		    if v == []:
			v = Variable(variablename)
			r.add_variable(v)
	
	# Add the filename to the variable list
	v.add_filename(name)
		
    return ens    
        