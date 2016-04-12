cmipdata
========

.. image:: https://zenodo.org/badge/doi/10.5281/zenodo.33229.svg
   :target: http://dx.doi.org/10.5281/zenodo.33229

Introduction
------------

**cmipdata** is a python package for preprocessing and analysis of climate model 
data in standardized NetCDF files, such as those used in the Coupled Model 
Intercomparison Project (CMIP). With cmipdata processing hundreds of NetCDF files 
that make up a large model ensemble is easy. **cmipdata** is the python wrapper 
that intelligently interfaces with the ensemble of model data, while the underlying 
data processing is done efficiently and transparently using 
`Climate Data Operators (cdo) <https://code.zmaw.de/projects/cdo>`_. 
Limited functionality for loading processed data into `numpy 
<http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=175103>`_ 
arrays and making basic plots is also provided. 

Common operations and some example analyses that can be applied across the whole 
model ensemble with only one or two commands are:

* joining model time-slices (or experiments)
* spatial remapping to a common grid
* selecting a specific time-interval or spatial region
* computing a climatology or an anomaly
* calculating an area mean or integral
* calculating more advanced metrics such as Arctic sea-ice extent

Documentation
-------------
Documentation is rendered at https://cmipdata.readthedocs.org and is included in the 
docs/ directory.

.. image:: https://readthedocs.org/projects/cmipdata/badge/?version=latest
   :target: https://readthedocs.org/projects/cmipdata/?badge=latest
   :alt: Documentation Status

Contributors
------------
Neil Swart, CCCma, Environment Canada: Neil.Swart@canada.ca

David Fallis, University of Victoria:  davidwfallis@gmail.com

Pull requests and comments are welcome.

LICENSE
-------

See the LICENSE.txt file in the cmipdata package. cmipdata is distributed
under the GNU General Public License version 2, and the Open Government 
License - Canada (http://data.gc.ca/eng/open-government-licence-canada)

