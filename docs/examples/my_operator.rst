.. _my_operator:

Custom cdo command
==================

You can apply any valid cdo command to the whole ensemble using the 
:func:`~cmipdata.my_operator` function. Chained cdo commands are allowed. In this 
example we will carry out several chained operations. Our objective is to get a 
time-anomalies of sea-ice for the period 1979 to 2013 relative to a base-period of 
1991 to 2000. We also want the result to be zonally meaned, and remapped onto a 
1-degree-latitude grid::

    import cmipdata as cd
    
    ens = cd.mkensemble('sic_OImon*')

    my_cdo_str = 'cdo remapdis,r1x180 -zonmean -seldate,1979-01-01,2013-12-31' +
                 '-sub {infile} -timmean -seldate,1991-01-01,2000-12-31 {infile}' +
                 '{outfile}'

    ens = cd.my_operator(ens, my_cdo_str, output_prefix='test_', delete=False)
    
The result is a set of files that begin with the prefix ``test_`, and an updated 
ensemble.     