"""loading_tools
======================

The loading_tools module of cmipdata is a set of functions which use
the cdo python bindings and NetCDF4 to load data from input NetCDF
files listed in a cmipdata ensemble object into python numpy arrays.
Some processing can optionally be done during the loading, specifically
remapping, time-slicing, time-averaging and zonal-averaging.

.. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>
"""
import cdo as cdo
cdo = cdo.Cdo()  # recommended import
import os
import numpy as np
from netCDF4 import Dataset, num2date, date2num
import datetime

# clean out tmp to make space for CDO processing.
os.system('rm -rf /tmp/cdo*')


def loadvar(ifile, varname, cdostr=None, **kwargs):
    """
        Load variables from a NetCDF file with optional pre-processing.

        Load a CMIP5 netcdf variable "varname" from "ifile" and an optional
        cdo string for preprocessing the data from the netCDF files.
        Requires netCDF4, CDO and CDO python bindings.
        Returns a masked array, var.
      """
    # Open the variable using NetCDF4 to get scale and offset attributes.
    nc = Dataset(ifile, 'r')
    ncvar = nc.variables[varname]
    
    # apply cdo string if it exists
    if(cdostr):
        opslist = cdostr.split()
        base_op = opslist[0].replace('-', '')
        if len(opslist) > 1:
            ops_str = ' '.join(opslist[1::]) + ' ' + ifile
            var = getattr(cdo, base_op)(input=ops_str, returnMaArray=varname)
        else:
            var = getattr(cdo, base_op)(input=ifile, returnMaArray=varname)

    else:
        var = cdo.readMaArray(ifile, varname=varname)

    # Apply any scaling and offsetting needed:
    try:
        var_offset = ncvar.add_offset
    except:
        var_offset = 0
    try:
        var_scale = ncvar.scale_factor
    except:
        var_scale = 1

    # var = var*var_scale + var_offset
    # return var
    return np.squeeze(var)


def _create_tempfile(ens, varname, ifileone, cdostr=None, **kwargs):
    """
        _create_tempfile is called when modifications are made to the ensemeble without
        creating new files. Creates a temporary file that can be used to determine dimensions of
        the modified data.
    """
    if(cdostr):
        opslist = cdostr.split()
        op = opslist[0].replace('-', '')
        cdo_str = 'cdo ' + op + ' ' + ifileone + ' temporary_0.nc'
        ex = os.system(cdo_str)
        if len(opslist) > 1:
            for i in range(1, len(opslist)):
                op = opslist[i].replace('-', '')
                cdo_str = 'cdo ' + op + ' ' + 'temporary_' + str(i-1) + '.nc' + ' temporary_' + str(i) + '.nc'
                ex = os.system(cdo_str)
                os.remove('temporary_' + str(i-1) + '.nc')
                if i == len(opslist)-1:
                    os.rename('temporary_' + str(len(opslist)-1) + '.nc', 'temp123.nc')
        else:
            os.rename('temporary_0.nc', 'temp123.nc')


def loadfiles(ens, varname, toDatetime=False, **kwargs):
    """
        Load a variable "varname" from all files in ens, and load it into a matrix
        where the zeroth dimensions represents an input file and dimensions 1 to n are
        the dimensions of the input variable. Variable "varname" must have the same shape
        in all ifiles. Keyword argument toDatetime (defaults to False) will be passed as 
        a keyword argument to get_dimensions(). Optionally specify any kwargs valid for loadvar.

        Requires netCDF4, cdo bindings and numpy
        
        Returns 
        -------
        dictionary with keys data and dimensions
             data maps to a numpy array containing the data
             dimensions has keys; models, realizations, 
                and possibly lat, lon, and time
        
    """
    # Get all input files from the ensemble
    files = ens.objects('ncfile')
    ifiles = []
    for f in files:
        ifiles.append(f.name)
    
    # if a cdostr is being applied, 
    # create a temporaryfile to determine the dimensions of the data
    if 'cdostr' in kwargs:
        _create_tempfile(ens, varname, ifiles[0], **kwargs)
        dimensions = get_dimensions('temp123.nc', varname, toDatetime=toDatetime)
        os.remove('temp123.nc')
    else:
        dimensions = get_dimensions(ifiles[0], varname, toDatetime=toDatetime)

    vst = loadvar(ifiles[0], varname, **kwargs)
    varmat = np.ones((len(ifiles),) + vst.shape) * 999e99

    for i, ifile in enumerate(ifiles):
        varmat[i, :] = loadvar(ifile, varname, **kwargs)

    varmat = np.ma.masked_equal(varmat, 999e99)
    
    models = get_models(files)
    realizations = get_realizations(files)
    dimensions['models'] = models
    dimensions['realizations'] = realizations
    return {"data": varmat, 
            "dimensions": dimensions,
            }

def get_models(files):
    models = []
    for f in files:
        models.append(f.parentobject('model').name)
    return models
    
def get_realizations(files):
    realizations = []
    for f in files:
        realizations.append(f.parentobject('realization').name)
    return realizations    

        
def get_dimensions(ifile, varname, toDatetime=False):
    """Returns the dimensions of variable varname in file ifile as a dictionary.
    If one of the dimensions begins with lat (Lat, Latitude and Latitudes), it
    will be returned with a key of lat, and similarly for lon. If toDatetime=True,
    the time dimension is converted to a datetime.
    """

    # Open the variable using NetCDF4
    nc = Dataset(ifile, 'r')
    ncvar = nc.variables[varname]

    dimensions = {}
    for dimension in ncvar.dimensions:
        if dimension.lower().startswith('lat'):
            dimensions['lat'] = nc.variables[dimension][:]
        elif dimension.lower().startswith('lon'):
            dimensions['lon'] = nc.variables[dimension][:]
        elif dimension.lower().startswith('time'):
            if toDatetime is True:
                # Following Phil Austin's slice_nc
                nc_time = nc.variables[dimension]
                try:
                    cal = nc_time.calendar
                except:
                    cal = 'standard'
                dimensions['time'] = num2date(nc_time[:], nc_time.units, cal)
                dimensions['time'] = [datetime.datetime(
                    *item.timetuple()[:6]) for item in dimensions['time']]
                dimensions['time'] = np.array(dimensions['time'])
            else:
                dimensions['time'] = nc.variables[dimension][:]
        else:
            dimensions[dimension] = nc.variables[dimension][:]
    return dimensions


if __name__ == "__main__":
    pass
