========
cmipdata
========

Introduction
------------

cmipdata is a Python package for preprocessing, analysis and plotting of climate model data
in standardized NetCDF files, such as those used in the Coupled Model Intercomparison Project (CMIP). 
With cmipdata processing hundreds of NetCDF files that make up a large model ensemble is easy 
and efficient. It contains three basic toolsets: 

1) *preprocessing_tools* allow a standard processing (e.g. remapping, concatenating time-slices, zonal-mean) to be 
   systematically applied across an ensemble of models, consisting of many realizations and individual files and 
   produces properly-named output files. The processing is done efficiently using Climate Data Operators (cdo). 

2) *loading_tools* facillitates loading data from the multiple files comprising the model ensemble into a single, logical
   numpy-based data-structure in python. 

3) *plotting_tools* provides quick methods for common plotting tasks (e.g. ensemble mean with envelope) using matplotlib.

Documentation
-------------
Documentation for the tools is included in the docs/ directory and is rendered at https://cmipdata.readthedocs.org

.. image:: https://readthedocs.org/projects/cmipdata/badge/?version=latest
   :target: https://readthedocs.org/projects/cmipdata/?badge=latest
   :alt: Documentation Status


Examples
--------

The surface temperature files of HadCM3 are provided in multiple slices for the historical experiment::

    >ls
    ts_Amon_HadCM3_historical_r1i1p1_185912-188411.nc
    ts_Amon_HadCM3_historical_r1i1p1_188412-190911.nc
    ts_Amon_HadCM3_historical_r1i1p1_190912-193411.nc
    ts_Amon_HadCM3_historical_r1i1p1_193412-195911.nc
    ts_Amon_HadCM3_historical_r1i1p1_195912-198411.nc
    ts_Amon_HadCM3_historical_r1i1p1_198412-200512.nc

First we load the cmipdata package, and build an ensemble object, simply matching the filenames::

     import cmipdata as cd
     ens = cd.mkensemble('ts_Amon_HadCM3*')

Next we use cat_exp_slices to join the sliced files::   

     ens = cd.cat_exp_slices(ens)         

and the result is one unified file, which has been appropriately named::

    >ls 
    ts_Amon_HadCM3_historical_r1i1p1_185912-200512.nc
                                
We were also returned an updated ensemble object, the structure of which we can view as follows::

     ens.fulldetails()

     HadCM3:
         historical
                 r1i1p1
                         ts
                                 ts_Amon_HadCM3_historical_r1i1p1_185912-200512.nc
                                
This example shows only one model, but the method works equally well for a large ensemble consisting
of multple models, each with multiple realizations and hundreds of files. For example, using::

     ens = cd.mkensemble('ts_Amon_*')
     
would build an ensemble consisting of all files in the present directory starting with ts_Amon, and join_exp_slices
would, on a per-realization basis, do the joining, when necessary.


Disclaimer
----------
WARNING: This package is in development and there are no guarantees whatsoever.

Contributors
------------
Neil Swart, CCCma, Environment Canada: Neil.Swart@ec.gc.ca

LICENSE
-------

See the LICENSE.txt file in the cmipdata package. cmipdata is distributed
under the GNU General Public License version 3, and the Open Government License - Canada 
(http://data.gc.ca/eng/open-government-licence-canada)

