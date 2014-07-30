"""
Tests of the loading_tools module of cmipdata.

Requires running test_preprocessing_tools first.

"""

import cmipdata as cd
import os

# first change to a scratch dir and link in test data. The paths are CCCma specific.
os.chdir('/home/ncs/ra40/cmipdata/test_preprocessing_tools')

# Create a cmipdata ensemble 
filepattern = 'test_ts_Amon*'
ens = cd.mkensemble(filepattern,prefix='test_')

data =  cd.loadfiles(ens, 'ts')
data.shape