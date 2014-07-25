import cmipdata as cd
import os

## Link the data into the PWD
##os.chdir('/home/ncs/ra40/cmipdata/areamean')
os.system('ln -s ../*.nc .')

## Create a cmipdata ensemble 
filepattern = 'ts_Amon*'
ens = cd.mkensemble(filepattern)

## Do area mean
area_mean_ens = cd.areamean(ens)
area_mean_ens.fulldetails()

# Join the experiment
ens = cd.cat_experiments(area_mean_ens, 'ts', 'historical', 'rcp85')


# time-slice the data
ens = cd.time_slice(ens, '1900-01-01','2020-12-31')



import cmipdata as cd
filepattern = 'ts_Amon*'
ens = cd.mkensemble(filepattern)
cd.ens_stats(ens, 'ts')