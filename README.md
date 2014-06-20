========
cmipdata
========

cmipdata is a python package designed to manipulate a large set of CMIP type netcdf model ouput files. 
It provides three basic types of functionality: 

1) perform a common processing (see available options below) on a list of input files, and write out the processed result to netcdf.

2) perform a common processing and load the result into python on the fly (no ouput files written).

3) provide standardized plots.

The most popular functionilty (from 1) is the ability to join multiple model time-slices into a single file, in a smart, per realization basis.  

cmipdata is a python wrapper which aims to ensure smart handling of the input files. All netcdf data processing is done by CDO, either as a system call,
or through the cdo python bindings in the case of 2) above. Plotting functionality uses matplotlib and basemap.

WARNING: This package is in development and there are no guarantees whatsoever.

Contributors
============
Neil Swart, CCCma, Environment Canada: Neil.Swart@ec.gc.ca

=====================
Structure and content
=====================
cmipdata/
   - climatology.py      : Create a monthly climatology and optionally remap to a gieven resolution (e.g. remap='r360x180') and optionally first select he time-slice between "start_date" and "end_date".      

   - ensmean.py          : Compute a "smart" ensemble mean, where each realization is appropriately weighted so that for each model the combined weight is 1.

   - ens_plot.py         : NOT generalized or working, but meant to plot a 1-d field across all realizations (e.g. zonal-mean time-mean sst).

   - join_exp_slices.py  
      - join_exp_slice   : concatenate time-slices for each model / realization in a given list of files / models.
      - match_exp        : for each realization of the historical experiment check if that realization exists for the RCP experiment, rcpname.
      
   - listfiles.py        : list all netcdf files, optionally which start with "varname" and are from "experiment".
   
   - loaddata.py         : use python cdo binding to remap and/or timemean and/or time-delimit the field and return the data structure into python as a numpy array OR else, just load the variable using netcdf4.
   
   - mload1d.py          : for a given set of files with 1-d, load the data into a numpy array, with each row representing an input file, and each column representig the 1-dimension (e.g. time, latitude etc).
   
   - remap_timelim.py            : remap to a gieven resolution (e.g. remap='r360x180') and optionally first select he time-slice between "start_date" and "end_date".      

   - areaweight.py       : not yet developed

   - areaint.py          : not yet developed

   - areamean.py         : not yet developed

   - zonmean.py          : compute and save the zonal mean for each file in a given list.


   --plot/
       - zonmean         : not yet developed
       - areaint         : not yet developed

=======
LICENSE
=======

See the LICENSE.txt file in the cmipdata package. cmipdata is distributed
under the GNU General Public License version 3, and the Open Government License - Canada 
(http://data.gc.ca/eng/open-government-licence-canada)


