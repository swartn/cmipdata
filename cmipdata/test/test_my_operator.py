import cmipdata as cd
import os

# Link the data into the PWD
#os.chdir('/home/ncs/ra40/cmipdata/areamean')


# Create a cmipdata ensemble 
filepattern = 'ts_Amon*'
ens = cd.mkensemble(filepattern)

# print out info on the ensemble, which has been updated
ens.fulldetails()
ens.sinfo()


# apply my_operator
my_cdo_str = 'cdo sub {infile} -timmean -seldate,1991-01-01,2000-12-31 {infile} {outfile}'


cd.my_operator(ens, my_cdo_str, output_prefix='test_', delete=False)
