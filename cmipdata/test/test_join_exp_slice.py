import cmipdata as cd
import os

# Link the data into the PWD
#os.chdir('/home/ncs/ra40/cmipdata/')
os.system('ln -s /ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon*historical*r1i1p1*.nc .')
os.system('ln -s /ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon*rcp85*r1i1p1*.nc .')

# Create a cmipdata ensemble 
filepattern = 'ts_Amon*'
ens = cd.mkensemble(filepattern)

# Join the experiment timeslices
ens = cd.cat_exp_slices(ens)

# print out info on the ensemble, which has been updated
ens.fulldetails()
ens.sinfo()

# join the historical and rcp85 experiment
ens2 = cd.cat_experiments(ens, 'ts', 'historical', 'rcp85')

# print out info on the ensemble, which has been updated
#ens2.fulldetails()
ens2.sinfo()


"""
import cmipdata as cd
filepattern = 'ts_Amon*bcc-csm1-1-m*'
ens = cd.mkensemble(filepattern)
ens2 = cd.cat_experiments(ens, 'ts', 'historical', 'rcp85')
"""

import cmipdata as cd
import os
os.system('rm -f *')
os.system('ln -s ../* .')

filepattern = 'ts_Amon*'
ens = cd.mkensemble(filepattern)
ens.sinfo()
ens2 = cd.cat_experiments(ens, 'ts', 'historical', 'rcp85')
#ens2.fulldetails()

