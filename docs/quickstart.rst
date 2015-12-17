**********
Quickstart
**********

Installing
===========

**Dependencies**

Several external packages are required:

`Python 2.7x <http://www.python.org/download/>`_

`Climate Data Operators (cdo) <https://code.zmaw.de/projects/cdo>`_ v1.6 or later.

`netCDF4 <http://unidata.github.io/netcdf4-python/>`_

`numpy 1.2.1 or later 
<http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=175103>`__

`matplotlib <http://sf.net/projects/matplotlib/>`_ 

cmipdata has primarily been developed and tested within the 
`anaconda <http://docs.continuum.io/anaconda/index.html>`_ python distribution on 
Linux x86/x64 and Mac OSX. Windows is not supported.

**Installation**

To install, first clone the repo from github:

.. code-block:: bash

    git clone https://github.com/swartn/cmipdata.git
    
then build and install:

.. code-block:: bash

    cd cmipdata
    python setup.py install
    
You can (should) do this inside a virtual environment. In that case it will work 
without root privileges. If you are using anaconda see  
http://conda.pydata.org/docs/faq.html#env.

Using cmipdata
==============

After a successful installation, you can import cmipdata as you would any other 
package in python:

.. code-block:: py

    import cmipdata as cd
    
The next step is to create an :class:`Ensemble`. :class:`Ensemble` objects are the 
structures used in cmipdata to organize climate model data. The assumption is that 
you have some CMIP-like netCDF model data on your local disk (cmipdata does not 
facillitate downloading data). For this example we have several hundred CMIP5 
sea-ice concentration files in our directory, downloaded from the ESGF. To create 
an ensemble object, simple use :func:`mkensemble`, specifing the filepattern to 
match:

.. code-block:: py

    In [2]: ens = cd.mkensemble('sic_OImon*')
    This ensemble contains:
     49 models 
     49 realizations 
     1 experiments 
     1 variables 
     279 associated files

 For more details use ens.fulldetails() 

The printout tells us some details about the data in our new ensemble. It consists 
of 49 models, 49 realizations, 1 experiment and 1 variable, all of which are also 
objects in the organizational paradigm of cmipdata (see :ref:`cmipdataAPI`). There 
are many more files than model or realizations, because for some models the 
experiment is broken up into multiple files, each representing a time-slice. In 
this example there is only one experiment (historical), but there could be many 
(if we had files for the RCPs experiments too). cmipdata provided the ability to 
join these multiple time-slice files together, and perform a host of other 
elaborate processing. 
