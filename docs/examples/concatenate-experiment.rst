.. _cat_experiments:

Concatenate experiments
=======================

The CMIP5 experimental design consisted of various experiments. Sometimes it is 
desirable to time-join experiments, for example, the historical and RCP4.5 
experiments can be join together for each realization from each model to provide a 
continuous time-series that runs from 1871 to 2100. The 
:func:`~cmipdata.cat_experiments` function provides this functionality. In this 
example we join the historical and RCP4.5 sea-ice extent fields for many models and 
realizations::

    import cmipdata as cd
    
    ens = cd.mkensemble('sic_OImon*')
    
        This ensemble contains:
            49 models 
           369 realizations 
             2 experiments 
             1 variables 
          1642 associated files

        For more details use ens.fulldetails() 

    ens_joined = cd.cat_experiments(ens, 'sic', 'historical', 'rcp45')
    
This operation takes some time, prints out progress along the way, and returns an 
updated ensemble. By default the input files will be deleted, and only the joined 
files will remain in our directory.
:func:`cat_experiments` takes care of doing 
joining of multiple time-slices within experiments, as well as joining the two 
experiments together. After this operation the number of files have been reduced, 
due to joining. The number of models or realizations in the returned ensemble may 
also be lower, because only models/realizations that have both a historical and 
RCP4.5 experiment available are retained. prints this information out for us::

    
 Models deleted from ensemble (missing one experiment completely): 

         Model   Experiment 

         CESM1-FASTCHEM          historical
         CESM1-CAM5-1-FV2        historical
         CNRM-CM5-2      historical
         MPI-ESM-P       historical
         CMCC-CESM       historical
         MRI-ESM1        historical
 

 Realizations deleted (missing from one experiment): 

         Model   Realizations 

         IPSL-CM5A-LR    r6i1p1 r5i1p1
         bcc-csm1-1-m    r2i1p1 r3i1p1
         GFDL-CM3        r2i1p1 r4i1p1
         ACCESS1-0       r2i1p1
         CNRM-CM5        r7i1p1 r9i1p1 r2i1p1 r10i1p1 r4i1p1 r3i1p1 r6i1p1 r5i1p1 
                         r8i1p1
         GISS-E2-H       r6i1p1 r6i1p3
         FGOALS-g2       r2i1p1 r4i1p1 r3i1p1 r5i1p1
         ACCESS1-3       r2i1p1 r3i1p1
         CCSM4   r1i2p1 r1i2p2
         HadGEM2-ES      r5i1p1
         GISS-E2-R       r1i1p128 r1i1p122 r1i1p121 r1i1p126 r1i1p127 r1i1p124 
                         r1i1p125 r6i1p2
         HadGEM2-CC      r2i1p1 r3i1p1
         MIROC-ESM       r2i1p1 r3i1p1
         EC-EARTH        r5i1p1
         MRI-CGCM3       r4i1p2 r2i1p1 r3i1p1 r5i1p2
         NorESM1-M       r2i1p1 r3i1p1
         bcc-csm1-1      r2i1p1 r3i1p1
         CESM1-WACCM     r1i1p1
         IPSL-CM5A-MR    r2i1p1 r3i1p1

We can use the :func:`~cmipdata.Ensemble.sinfo` command to get an update on what 
the returned ensmble looks like::

    ens_joined.sinfo()
    This ensemble contains:
     43 models 
     153 realizations 
     1 experiments 
     1 variables 
     153 associated files

After the joining we can now see that there is one file per realization. 




