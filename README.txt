Introduction:

-------------

cmipdata is a python package designed to manipulate a large set of CMIP type netcdf model ouput files. It provides three basic types of functionality: 

1) perform a common processing (see available options below) on a list of input files, and write out the processed result to netcdf.

2) perform a common processing and load the result into python on the fly (no ouput files written).

3) provide standardized plots.

The most popular functionilty (from 1) is the ability to join multiple model time-slices into a single file, in a smart, per realization basis.  

cmipdata is a python wrapper which aims to ensure smart handling of the input files. All netcdf data processing is done by CDO, either as a system call,
or through the cdo python bindings in the case of 2) above. Plotting functionality uses matplotlib and basemap.

-------------

Structure and content

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
-------------

LICENSE:
See the LICENSE.txt file in the cmipdata package. cmipdata is distributed
under the GNU General Public License version 3, and the Open Government License - Canada 
(http://data.gc.ca/eng/open-government-licence-canada)


