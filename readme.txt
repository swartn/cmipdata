This cmipdata package is designed to allow maniupulation of a group of CMIP5 datafiles that need to undergo a common processing. There is the ability to list all files of a given variable and experiment (listfiles), to concatenate all files in time (join_exp_slice), to remap files to a common grid, to create zonal-means, area-weighted means and integrals.

Structure

cmipdata/
   - listfiles.py        : list all netcdf files, optionally which start with "varname" and are from "experiment".
   - join_exp_slices.py  : concatenate time-slices for each model / realization in a given list of files / models.
   - join_exp.py         : join two experiments ( e.g. historical and rcp45 ) for each model in a given list of files.
   - zonmean.py          : compute and save the zonal mean for each file in a given list.
   - timlim.py           : compute and save the time-slice between "start_date" and "end_date".
   - remap.py         
   - areaweight.py
   - areaint.py
   - areamean.py
   - load_data.py

   --plot/
       - zonmean
       - areaint







