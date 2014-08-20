"""classes
======================

Summary
-------

The core functionality of cmipdata is to organize a large number of
model output files into a logical structure so that further processing
can be done. Data is organized into Ensembles, which are made up of many
Models, Experiments, Realizations and Variables and filenames. The structure treats 
`Variable`s as the lowest organizing theme. Each Variable contains a list of filenames 
(and other attributes), and each variable belongs
to a specified Realiation. Each Realization in turn belongs to a specified
Experiment, which will belong to a given Model.  
  
Various methods exist to interact with the Ensemble, and its constituent
elements. Once created, an Ensemble can be used to harness the power of
the `preprocessing_tools` to apply systematic operations to all files.
Indeed, all data-handling and processing in cmipdata used the Ensemble.

See Also
--------
 - preprocessing_tools
 - loading_tools
 - plotting_tools
  
Examples
-----------

A cmipdata Ensemble is easily created using:: 

    ens = cmipdata.mk_ensemble(filepattern) 

which generates the Ensemble `ens`, with all the underlying
structure, simply by matching all files matching the descriptor
`filepattern`.

A summary of the Ensemble can then be generated using::

    ens.sinfo()
    
and a full description of the Ensemble can be gained from::

    ens.fulldetails()

.. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>
"""

import os
import glob
import copy

class Ensemble(object):
    """ Defines a cmipdata Ensemble. 
       
    Attributes
    ----------
    models : list
             The list of constituent models
             
    """
    def __init__(self):
        self.models = []    
        
    def __str__(self):
        return "Models in %s: \n %s" %(self.name, '\n'.join([m.name for m in self.models]))
        
    def add_model(self, model):
	"""Add model to the ensemble
	
	Parameters
	----------
	model : cmipdata Model
	"""
        self.models.append(model)
        
    def del_model(self, model):
	"""Delete model from the ensemble
	
	Parameters
	----------
	model : cmipdata Model		
	"""
        self.models.remove(model)     
        
    def get_model(self, modelname):
        """Return modelname from the ensemble
	
	Parameters
	----------
	modelname : str
	            The name of the model to return
	            
	Returns 
	-------
	model : cmipdata Model
	        The Model object corresponding to 
	        modelname
    
	"""
	for model in self.models:
	    if model.name == modelname:
		m = model
		break
	else:
	    m = []
	return m

    def iterate(self):
	"""Returns a iterable, which is a tuple containing all the ensembles 
	model, experiment, realization and variable objects and the list of filenames.
	
	Examples
	-------
	
	Iterate over all files in ens::
	
           for model, experiment, realization, variable, files in ens.iterate():
               print model.name, experiment.name, realization.name, variable.name, files
               
	"""
	output = []
	for model in self.models:
	    for experiment in model.experiments:
		for realization in experiment.realizations:
		    for variable in realization.variables:
			output.append( (model, experiment, realization, variable, variable.filenames) )
			
        return iter(output)			
			
    def squeeze(self):
	""" Remove any empty elements from the ensemble
	WARNING: since ens is modifying itself in the loop, something could go wrong!
	"""
        for model, experiment, realization, variable, files in self.iterate():
	    realization.del_variable(variable) if variable.filenames == [] else 0 # if the variable contains no files delete it
   	    experiment.del_realization(realization) if realization.variables == [] else 0 # if the realization contains no variables delete it
   	    model.del_experiment(experiment) if experiment.realizations == [] else 0 # if the experiment contains no realizations delete it
   	    self.del_model(model) if model.experiments == [] else 0 # if the model contains no experiments delete it

   	return self
   	    
    def models(self):
	"""Retuns the list of model objects in the ensemble"""
        return self.models

    def num_models(self):
	""" Returns the number of models in the ensemble"""
        return len(self.models)
        
    def sinfo(self):
	""" Returns the number of models, experiments, realizations, variables and files 
	in the ensemble"""
        realizations=[] ; experiments=[]; variables=[]; files=[]
      	for m in self.models:
	    for e in m.experiments:
		experiments.append(e.name)
         	for r in e.realizations:
                    realizations.append(r.name)
		    for v in r.variables:
			variables.append(v.name)
		        for f in v.filenames:
			    files.append(f)

        rstring = "This ensemble contains:\n %s models \n %s realizations \n %s experiments \n %s variables \n %s associated files"\
            %( len(self.models), len(realizations), len(set(experiments)), len(set(variables)), len(files) ) 		
                 
        print rstring        
       
    
    def fulldetails(self):
	""" prints information about the number of models, experiments and realizations in an ensemble"""
	for model in self.models:
	    print model.name +':'
	    for experiment in model.experiments:
                print '\t' + experiment.name
		for realization in experiment.realizations:
		    print '\t\t' + realization.name
	            for variable in realization.variables:
		        print '\t\t\t' + variable.name
			for filename in variable.filenames:
			    print '\t\t\t\t' + filename     
                
class Model(object):
    """ Defines a model with a name.
    """
    def __init__(self, modelname):
        self.name = modelname
        self.experiments = []
               
    def add_experiment(self, experiment):
	"""Adds experiment to the model
	
	Parameters
	----------
	experiment : cmipdata Experiment
	
	"""
        self.experiments.append(experiment)
        
    def del_experiment(self, experiment):
	"""deletes experiment from the model"""
        self.experiments.remove(experiment)
        
    def get_experiment(self, experimentname):
	"""Returns the experiment with experimnentname.
	
	Parameters
	----------
	experimentname : string
	
	Returns
	----------
	experiment : cmipdata Experiment
	             The cmipdata experiment corresponding to 
	             experimentname for the model. If no experiment
	             matching experimentname is found, returns an
	             empty list.
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
        
    def num_experiments(self):
	""" Returns the number of experiments defined for the model"""
        return len(self.experiments)     

class Experiment(object):
    """ Defines an experiment for a given model. 
    
    Assiciated realizations can be retrieved with
    experiment.realizations(). New realizations can be added
    to the experiment with experiment.add_realization(realization)
    
    Parameters
    ----------
    experimentname : string
        
    Attributes
    ----------
    realizations : list
                   List of constituent realizations   
    
    """
    def __init__(self, experimentname):
        self.name = experimentname
        self.realizations = []
        
    def __str__(self):
        return self.name
        
    def add_realization(self, realization):
	"""Adds realization to the experiment."""	
        self.realizations.append(realization)
        
    def del_realization(self, realization):
	"""Deletes realization from the experiment."""	
        self.realizations.remove(realization)
        
    def get_realization(self, realizationname):
        """Returns the realization with realizationname. 
        
	Parameters
	----------
	realizationname : string
	
	Returns
	----------
	realization : cmipdata Realization
	             The cmipdata realization corresponding to 
	             realizationname for the experiment. If no realization
	             matching realizationname is found, returns an
	             empty list.        
        
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
        
    def num_realizations(self):
	""" Returns the number of realizations defined for the 
	experiment instance"""
        return len(self.realizations)  
        
class Realization(object):
    """ Defines a realization for a given model and experiment.
        
    Associated variables can be retrieved with
    realization.variables(). New variables can be added
    to the realization with realization.add_variable(variable)
    
    Parameters
    ----------
    realizationname : string
        
    Attributes
    ----------
    variables : list
                List of constituent variables     
    
    """
    def __init__(self, realizationname):
        self.name = realizationname
        self.variables = []
        
    def add_variable(self, variable):
	"""Adds variable object to the realization."""	
        self.variables.append(variable)
        
    def del_variable(self, variable):
	"""Deletes variable from the realization."""	
        self.variables.remove(variable)
        
    def get_variable(self, variablename):
        """Returns the variable object with variablename.
        
	Parameters
	----------
	variablename : string
	
	Returns
	----------
	variable : cmipdata Variable
	             The cmipdata variable corresponding to 
	             variablename for the realization. If no variable
	             matching variablename is found, returns an
	             empty list.        
              
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
        
    def num_variables(self):
	""" Returns the number of variables defined for the 
	realization instance"""
        return len(self.realizations)
        
class Variable(object):
    """Defines a variable for a given model, experiment and realization.
     
    Associated filenames can be retrieved with variable.filenames(). A new 
    filename can be added with variable.add_filename('filename.nc').
    
    Parameters
    ----------
    variablename : string
        
    Attributes
    ----------
    filenames : list
                List of constituent files                
    start_dates : list
                  List of start_dates of files in filenames.
    end_dates : list
                List of end_dates of files in filenames.                  
    """
    def __init__(self, variablename):
        self.name = variablename      
        self.filenames = []
        self.start_dates = []
        self.end_dates = []
        
    def add_filename(self, filename):
	"""Adds filname to the variable's list of files"""
        self.filenames.append(filename)
        
    def del_filename(self, filename):
	"""Removes a filname from the variable's list of files"""
        self.filenames.remove(filename)
        
    def add_realm(self, realm):
	"""Adds realm to the variable"""
        self.realm = realm  
        
    def add_start_date(self, start_date):
	"""Adds start_dates to the variable's list of file start-dates"""
        self.start_dates.append(start_date)  
        
    def add_end_date(self, end_date):
	"""Adds end_date to the variable's list of file end-dates"""
        self.end_dates.append(end_date) 
        
    def filenames(self):
        """ Retuns a list of filenames associated with the variable"""	
        return self.filenames
        
    def num_files(self):
	""" Returns the number of files listed for the 
        variable instance"""
        return len(self.filenames)        
   
def mkensemble(filepattern, experiment='*', prefix='', kwargs=''):
    """Creates and returns a cmipdata ensemble object from a list of 
    filenames matching filepattern. 

    Optionally specifying prefix will remove prefix from each filename
    before the parsing is done. This is useful, for example, to remove 
    pre-pended paths used in filepattern (see example 2).
    
    Once the list of matching filenames is derived, the model, experiment,
    realization, variable, start_date and end_date fields are extracted by
    parsing the filnames against a specified file naming convention. By 
    default this is the CMIP5 convention, which is::
    
        variable_realm_model_experiment_realization_startdate-enddate.nc
    
    If the default CMIP5 naming convention is not used by your files,
    an arbitary naming convention for the parsing may be specified by
    the dicionary kwargs (see example 3). 
    
    
    Parameters
    ----------
    
    filepattern : string  
                A string that by default is matched against all files in the 
                current directory. But filepattern could include a full path 
                to reference files not in the current directory, and can also 
                include wildcards. 
                
    prefix : string
             A pattern occuring in filepattern before the start of the official
             filename, as defined by the file naming converntion. For instance,
             a path preceeding the filename.
    
    EXAMPLES
    --------
    
    1. Create ensemble of all sea-level pressure files from the historical experiment in 
    the current directory::
    
        ens = mkensemble('psl*historical*.nc') 
          
    2. Create ensemble of all sea-level pressure files from all experiments in a non-local
    directory::
    
        ens = mkensemble('/home/ncs/ra40/cmip5/sam/c5_slp/psl*'
                      , prefix='/home/ncs/ra40/cmip5/sam/c5_slp/') 

    3. Create ensemble defining a custom file naming convention::
    
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
	    v.add_realm(realm)
	    r.add_variable(v)
			
	# Add the filename to the variable list
	v.add_filename(prefix + name)
	v.add_start_date(start_date)
	v.add_end_date(end_date)
	
    ens.sinfo()
    print('\n For more details use ens.fulldetails() \n')
    return ens    
    
def match_ensembles(ens1, ens2):
    """
    Find common models between two ensembles.
    
    Parameters
    ----------
    ens1 : cmipdata ensemble
    ens2 : cmipdata ensemble
           the two cmipdata ensembles to compare.
    
    Returns
    ------- 
    ens1 : cmipdata ensemble
    ens2 : cmipdata ensemble
    
    """
    # Get the modelnames
    ens1_modelnames = [ model.name for model in ens1.models]
    ens2_modelnames = [ model.name for model in ens2.models]
    
    # find matching and non-matching models 
    model_matches = set( ens1_modelnames ).intersection( ens2_modelnames )
    model_misses = set( ens1_modelnames ).symmetric_difference( ens2_modelnames )
    
    #print model_misses
    #print len(model_matches), model_matches
    
    # remove non-matching models
    for name in model_misses:
        m = ens1.get_model(name)
	if m !=[]:
            print 'deleting %s from ens1' %(m.name)
	    ens1.del_model(m)
	    
	m = ens2.get_model(name)
	if m !=[]:
	    print 'deleting %s from ens2' %(m.name)
	    ens2.del_model(m)
    	    
    return ens1, ens2	
	

		    