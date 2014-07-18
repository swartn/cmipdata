import cmipdata as cd
#(filenames, modelnames) = cd.listfiles('/home/ncs/ra40/cmip5/sam/c5_slp/zonmean_psl_Amon_*_2013')
path='/home/ncs/ra40/cmip5/sam/c5_slp/'
f = open(path+'list_match_uas','r')
filenames = [ line.strip() for line in f ]
filenames = [ path + f for f in filenames ]

kwargs={'start_date':'1979-01-01', 'end_date':'2009-12-31'} #, 'timmean':True}
mat = cd.loadfiles( filenames, 'psl', **kwargs)

print mat.shape