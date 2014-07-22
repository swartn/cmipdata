class Ensemble(object):
    """ Defines an ensemble with a name.
    """
    def __init__(self, ensemblename):
        self.name = ensemblename
        self.models = []    
        
    def __str__(self):
        return "Models in %s: \n %s" %(self.name, '\n'.join([m.name for m in self.models]))
        
    def num_models(self):
        return len(self.models)

    def add_model(self, modelname):
        self.models.append(modelname)
        
    def get_model(self, modelname):
	for model in self.models:
	    if model.name == modelname:
		m = model
		break
	else:
	    m = []
	return m
	
    def models(self):
        return self.models
        
class Model(object):
    """ Defines a model with a name.
    """
    def __init__(self, modelname):
        self.name = modelname
        self.experiments = []
               
    def add_experiment(self, experimentname):
        self.experiments.append(experimentname)

    def get_experiment(self, experimentname):
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
        self.realizations.append(realization)
        
    def get_realization(self, realizationname):
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
        self.variables.append(variable)
        
    def get_variable(self, variablename):
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
        
    def add_filename(self, fn):
        self.filenames.append(fn)
        
    def filenames(self):
        return self.filenames
        
             
        
        