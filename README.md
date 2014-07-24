========
cmipdata
========

Introduction
------------

cmipdata is a python package designed to facilliate preprocessing, analysis and plotting of climate model data
in standardized NetCDF files, such as those used in the Coupled Model Intercomparison Project (CMIP). 
It contains three basic toolsets: 

1) *preprocessing_tools* allow a standard processing (e.g. remapping, concatenating time-slices, zonal-mean) to be 
   systematically applied across an ensemble of models, consisting of many realizations and individual files and 
   produces properly-named output files. The processing is done efficiently using climate data operators. 

2) *loading_tools* facillitates loading data from the multiple files comprising the model ensemble into a single, logical
   numpy-based data-structure in python. 

3) *plotting_tools* provides quick methods for common plotting tasks (e.g. ensemble mean with envelope) using matplotlib.


Examples
--------

1) The surface temperature files of HadCM3 are provided in multiple slices for the historical experiment: 

                                ts_Amon_HadCM3_historical_r1i1p1_185912-188411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_188412-190911.nc
                                ts_Amon_HadCM3_historical_r1i1p1_190912-193411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_193412-195911.nc
                                ts_Amon_HadCM3_historical_r1i1p1_195912-198411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_198412-200512.nc

To join them we call cat_exp_slices, which we pass a cmipdata ensemble object.

     ens = cd.cat_exp_slices(ens)         

and the result is one unified file, which has been appropriately named:     
     
                                ts_Amon_HadCM3_historical_r1i1p1_185912-200512.nc

This example shows only one model, but the method works equally well for a large ensemble consisting
of multple models, each with multiple realizations and hundreds of files. 

Disclaimer
==========
WARNING: This package is in development and there are no guarantees whatsoever.

Contributors
============
Neil Swart, CCCma, Environment Canada: Neil.Swart@ec.gc.ca



LICENSE
=======

See the LICENSE.txt file in the cmipdata package. cmipdata is distributed
under the GNU General Public License version 3, and the Open Government License - Canada 
(http://data.gc.ca/eng/open-government-licence-canada)

