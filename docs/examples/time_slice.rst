.. _time_slice:

Time slice
==========

Choose a common time slice out of all the CMIP5 sea ice concentration files in 
our directory::

    import cmipdata as cd
    ens = cd.mkensemble('sic_OImon*')
    ens = cd.time_slice(ens, start_date='1979-01-01', end_date='2013-12-31')

where ``start_date`` and ``end_date`` are given in YYYY-MM-DD format. This will 
create a new set of files covering the chosen period, and by default will delete 
the original input files (to prevent this specify ``delete=False``). Any 
realizations that do not contain the full requested date range will be dropped from 
the ensemble (and deleted by default).
    