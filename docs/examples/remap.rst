.. _remap:

remap
=====

To remap of all the sea ice concentration (sic) files in our directory to a common 
one-degree by one-degree grid, simply do::

    import cmipdata as cd
    
    ens = cd.mkensemble('sic_OImon*')    
    ens = cd.remap(ens, remap='r360x180')

The string given to remap is any valid remapping option that can be given to cdo. 
For example, you could give the name of a target grid file to remap to. The 
:func:`~cmipdata.remap` function also allows you to choose the remapping method, 
but distance weighted remapping is used by default.