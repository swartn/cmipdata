import cmipdata as cd

fp = '/ra40/data/ncs/fco2/cmipdata/zonal_time_means_fgco2_Omon_*'
ens = cd.mkensemble(fp,prefix='/ra40/data/ncs/fco2/cmipdata/zonal_time_means_')

fp2 = '/home/ncs/ra40/cmip5/sam/c5_sfcWind2/remap_zonal-mean_sfcWind*'
ens2 = cd.mkensemble(fp2, prefix='/home/ncs/ra40/cmip5/sam/c5_sfcWind2/remap_zonal-mean_')

enso1, enso2 = cd.match_ensembles(ens, ens2)
enso1.sinfo()
enso2.sinfo()

