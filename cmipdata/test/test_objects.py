import cmipdata as cd
filepattern = '/home/ncs/ra40/cmip5/sam/c5_slp/zonmean_psl_Amon_*historical_r1i1p1*.nc'
prefix = '/home/ncs/ra40/cmip5/sam/c5_slp/zonmean_'
ens = cd.mkensemble(filepattern, prefix=prefix)


kwargs = {'separator':'_', 'variable':0, 'realm':1, 'model':2, 'experiment':3,
    'realization':4, 'dates':5}
    
ens = cd.mkensemble(filepattern, prefix=prefix, kwargs=kwargs)


ens.fulldetails()



