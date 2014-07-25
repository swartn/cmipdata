import cmipdata as cd
import os

## Link the data into the PWD
##os.chdir('/home/ncs/ra40/cmipdata/areamean')

## Create a cmipdata ensemble 
filepattern = 'ts_Amon*'
ens = cd.mkensemble(filepattern)

ens = cd.my_operator(ens, 'cdo -yearmean', output_prefix='annual_')
ens = cd.time_anomaly(ens, '1980-01-01','2010-12-31')
#cd.ens_stats(ens,'ts')

data = cd.loadfiles(ens,'ts') 

cd.plot_realization_timeseries(ens, data, 'ts')

ax = plt.gca()

cd.ensemble_envelope_timeseries(ens, 'ENS-MEAN_ts_Amon_historical-rcp85_190001-202012.nc', 'ENS-STD_ts_Amon_historical-rcp85_190001-202012.nc', 'ts', ax=ax)

canesm2_ens = cd.mkensemble('anomaly_ts_Amon_CanESM2*',prefix='anomaly_')
canesm2_data = cd.loadfiles(canesm2_ens,'ts') 
cd.plot_realization_timeseries(canesm2_ens, canesm2_data, 'ts', kwargs={'color':'g','linewidth':2})
