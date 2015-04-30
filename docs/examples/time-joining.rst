.. _cat_exp_slices:

Concatenate model time-slices
=============================

In this example we have the surface temperature files for HadCM3 in our directory, 
which are provided in six time-slices for the historical experiment, as the files:

 - ts_Amon_HadCM3_historical_r1i1p1_185912-188411.nc
 - ts_Amon_HadCM3_historical_r1i1p1_188412-190911.nc
 - ts_Amon_HadCM3_historical_r1i1p1_190912-193411.nc
 - ts_Amon_HadCM3_historical_r1i1p1_193412-195911.nc
 - ts_Amon_HadCM3_historical_r1i1p1_195912-198411.nc
 - ts_Amon_HadCM3_historical_r1i1p1_198412-200512.nc

To join them we can use the :func:`cat_exp_slices` function from cmipdata:: 

     import cmipdata as cd
     ens = cd.mkensemble('ts_Amon_HadCM3*')
     ens = cd.cat_exp_slices(ens)         

The result is one unified file in our directory, which has been appropriately named.
By default the individual time-slice fields will be deleted, and only 
the joined file is left in our directory. We can change this by passing the 
``delete=False`` option to :func:`cat_exp_slices`. We were also returned an updated 
ensemble object, the structure of which we can view as follows::

     ens.fulldetails()

     HadCM3:
         historical
                 r1i1p1
                         ts
                                 ts_Amon_HadCM3_historical_r1i1p1_185912-200512.nc
                                
Note that the joined file has been named in such a way that the start and end dates 
cover the full range of the input files.

This example shows only one model, but the method works equally well for a large 
ensemble consisting of multple models, each with multiple realizations and hundreds 
of files. For example, using::

     ens = cd.mkensemble('ts_Amon_*')
     
would build an ensemble consisting of all files in the present directory starting 
with ts_Amon, and join_exp_slices would, on a per-realization basis, do the 
joining, when necessary.
