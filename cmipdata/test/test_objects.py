import cmipdata as cd

(filenames, modelnames) = cd.listfiles('/home/ncs/ra40/cmip5/sam/c5_slp/zonmean_psl_Amon_*_r1i1p1')
#(filenames2, modelnames) = cd.listfiles('/home/ncs/ra40/cmip5/sam/c5_uas/zonmean_uas*historical_r1i1p1')

ens = cd.Ensemble('testensemble')

prefix = '/home/ncs/ra40/cmip5/sam/c5_slp/zonmean_'
for name in filenames:
    name = name.replace(prefix,'')
    variablename = name.split( '_' )[0]
    realm        = name.split( '_' )[1]
    modelname    = name.split( '_' )[2]
    experment   = name.split( '_' )[3]
    realization  = name.split( '_' )[4]
    dates        = name.split( '_' )[5]
    start_date   = int( name.split( '_' )[5].split('-')[0]) 
    end_date     = int( name.split( '_' )[5].split('-')[1].split('.')[0] )

    # create the model if necessary
    m = ens.get_model(modelname)   
    if m == []:
        m = cd.Model(modelname)
        ens.add_model(m)
    # create the experiment if necessary    
    e = m.get_experiment(experiment)   
    if e == []:
        e = cd.Experiment(experiment)
        m.add_experiment(e)
    #create the realization if necessary
    r = e.get_realization(realization)   
    if r == []:
        r = cd.Realization(realization)
        e.add_realization(r)
    # create the variable if necessary    
    v = r.get_variable(variablename)   
    if v == []:
        v = cd.Variable(variablename)
        r.add_variable(v)
        
    v.add_filename(name)
   
    #print ens.models[-1].name +':' + '\n \t' + ','.join([e.name for e in ens.models[-1].experiments])  + '\n' + ','.join([ fn for fn in m.experiments[-1].realizations[-1].variables[-1].filenames]) +'\n'
 
    
#filename = prefix+name


for model in ens.models:
    print model.name +':'
    for experiment in model.experiments:
	print '\t' + experiment.name
	for realization in experiment.realizations:
	    print '\t\t' + realization.name
	    for variable in realization.variables:
	        print '\t\t\t' + variable.name
	        for filename in variable.filenames:
		    print '\t\t\t\t' + filename


#co = cd.cmipdata(filename, variablename, realm, modelname, experiment, realization, start_date, end_date) 

