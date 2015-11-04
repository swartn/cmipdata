.. cmipdata documentation master file, created by
   sphinx-quickstart on Wed Jul 30 15:46:24 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the cmipdata documentation!
======================================

**cmipdata** is a python package for preprocessing large ensembles of climate 
model data in standardized NetCDF files, such as those used in the Coupled Model 
Intercomparison Project (CMIP). The primary usage is to process 
the raw netCDF data from many models/realizations/experiments into a useful form 
for further analysis (e.g. by time-joining or slicing, remapping, averaging etc). 
**cmipdata** is the python wrapper that intelligently interfaces with the ensemble 
of model data, while the underlying data processing is done efficiently and 
transparently using `Climate Data Operators (cdo) 
<https://code.zmaw.de/projects/cdo>`_. Limited functionality for loading processed 
data into `numpy 
<http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=175103>`_ 
arrays and making basic plots is also provided.  

Contents:

.. toctree::
   :maxdepth: 1
  
   quickstart
   examples/index.rst
   api
   
Contributors
------------
Neil Swart, CCCma, Environment Canada: Neil.Swart@ec.gc.ca
David Fallis: davidwfallis@gmail.com

Pull requests and comments are welcome.

LICENSE
-------

See the LICENSE.txt file in the cmipdata package. cmipdata is distributed
under the GNU General Public License version 2, and the Open Government 
License - Canada (http://data.gc.ca/eng/open-government-licence-canada)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`





