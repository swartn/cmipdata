cmipdata
========

Introduction
------------
cmipdata is a Python package for preprocessing and analysis of climate model data
in standardized NetCDF files, such as those used in the Coupled Model Intercomparison Project (CMIP). 
With cmipdata processing hundreds of NetCDF files that make up a large model ensemble is easy 
and very efficient. The underlying netCDF operations are done using 
[Climate Data Operators](https://code.zmaw.de/projects/cdo), and cmipdata acts as a python
wrapper that facilliates performing common operations on a large ensemble of similar data files.

cmipdata provides tools to join timeslices, regrid, subsample and perform any aribitrary 
analysis that can be done by chaining cdo operators. Examples of possible analyses include
calculating quantities, over the whole model ensemble, such as:
 
  - Arctic sea ice extent
  - Global air-sea carbon fluxes
  - zonal mean winds during December

Documentation
-------------
Documentation for the tools is included in the docs/ directory and is rendered at https://cmipdata.readthedocs.org

.. image:: https://readthedocs.org/projects/cmipdata/badge/?version=latest
   :target: https://readthedocs.org/projects/cmipdata/?badge=latest
   :alt: Documentation Status

Contributors
------------
Neil Swart, CCCma, Environment Canada: Neil.Swart@ec.gc.ca

Contributions and comments are welcome.

LICENSE
-------

See the LICENSE.txt file in the cmipdata package. cmipdata is distributed
under the GNU General Public License version 3, and the Open Government License - Canada 
(http://data.gc.ca/eng/open-government-licence-canada)

