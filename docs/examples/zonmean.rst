.. _zonmean:

Zonal mean
==========

To create a zonal mean of all the sea ice concentration (sic) files, simply do::

    import cmipdata as cd
    
    ens = cd.mkensemble('sic_OImon*')
    ens = cd.zonmean(ens,delete=False)
    
    