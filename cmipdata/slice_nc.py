###
"""
   Get a [time,lat,lon] slice from a netcdf file
"""
import numpy as np
from netCDF4 import Dataset, num2date, date2num
import datetime as dt
import nose


def find_index(vec_vals, target):
    """

    returns the first index of vec_vals that contains the value
    closest to target.

    Parameters
    ----------

    vec_vals: list or 1-d array
    target:   list 1-d array or scalar


    Returns
    -------

    list of len(target) containing the index idx such that
    vec_vals[idx] is closest to each item in target

    Example
    -------

    >>> lons=[110,115,120,125,130,135,140]
    >>> find_index(lons,[115.4,134.9])
    [1, 5]

    """

    # turn scalar into iterable, no-op if already array
    target = np.atleast_1d(target)
    # turn list into ndarray or no-op if already array
    vec_vals = np.array(vec_vals)
    index_list = []
    for item in target:
        first_index = np.argmin(np.abs(vec_vals - item))
        index_list.append(first_index)
    return index_list


def get_var_2D(file_name, var_name, corners=None, start_date=None, stop_date=None,
               time_name='time', lat_name='lat', lon_name='lon'):
    """

    Given a netcdf file containing a [time,lat,lon] variable with name
    var_name, return a slice with values
    [start_date:stop_date,corners.ll.lat:corners.ur.lat,corners.ll.lon:corners.ur.lon]

    Parameters
    ----------

    filename: str --  name of netcdf (possible including full path) of netcdf file
    varname:  str --  name of [time,lat,lon] netcdf variable (.eg. tos)
    corners:  optional, my_namedtuple -- Box object with latlon corner points
                 if None, defaults to all lats, all lons
    start_date: optional, datetime  -- python datetime object to start slice
                 if None, defaults to time index 0
    stop_date: optional, datetime  -- python datetime object to end slice
                 if None, defaults to last time value

    Returns
    -------

    tuple containing:

    data_nc: netCDF4 Dataset
    var_nc:  netCDF4 variable
    the_times: np.array of datetimes for slice
    the_lats: 1-D np.array of latitudes for slice
    the_lons: 1_D np.array of longitudes for slice
    vararray: 2:D np.array with variable slice

    Example
    -------

    >>> from constants import warm_pool
    >>> in_file='tos_AMSRE_L3_v7_200206-201012.nc'
    >>> options=dict(corners=warm_pool,start_date=dt.datetime(2003,4,1),stop_date=dt.datetime(2006,3,1))
    >>> data_nc,var_nc,the_times,the_lats,the_lons,sst=get_var_2D(in_file,'tos',**options)
    >>> print(["%6.3f" % item for item in sst[0,0,:4]])
    ['301.819', '301.879', '301.970', '302.070']

    """
    data_nc = Dataset(file_name)
    var_nc = data_nc.variables[var_name]
    lat_nc = data_nc.variables[lat_name]
    lon_nc = data_nc.variables[lon_name]
    if corners is not None:
        #
        # get all the lats and lons
        #
        lats = lat_nc[...]
        lons = lon_nc[...]
        crn = corners
        #
        # lat/lon points of box corners are stored in a named_tuple
        # in constants.py
        #
        lat_slice = find_index(lats, [crn.ll.lat, crn.ur.lat])
        lat_slice[1] += 1
        lon_slice = find_index(lons, [crn.ll.lon, crn.ur.lon])
        lon_slice[1] += 1
    else:
        lat_slice = [0, None]
        lon_slice = [0, None]

    lat_slice = slice(*lat_slice)
    lon_slice = slice(*lon_slice)

    the_lats = lat_nc[lat_slice]
    the_lons = lon_nc[lon_slice]
    #
    # first convert to netcdftime datetime objects
    #
    time_nc = data_nc.variables['time']
    the_times = time_nc[...]
    the_dates = num2date(the_times, time_nc.units, time_nc.calendar)
    #
    # netCDF4 bug(?) means that netcdftime objects can't be compared/sorted
    # so convert to python datetime objects
    #
    py_dates = [dt.datetime(*item.timetuple()[:6]) for item in the_dates]
    py_dates = np.array(py_dates)
    #
    #
    #
    if start_date is None:
        start_index = 0
    else:
        start_index = find_index(py_dates, start_date)[0]
    if stop_date is not None:
        stop_index = find_index(py_dates, stop_date)[0]

    time_slice = slice(start_index, stop_index)
    the_times = py_dates[time_slice]
    var_array = var_nc[time_slice, lat_slice, lon_slice]
    return data_nc, var_nc, the_times, the_lats, the_lons, var_array


def test_get_var_2D():
    from constants import warm_pool as wp
    import numpy.testing as nt
    in_file = 'tos_AMSRE_L3_v7_200206-201012.nc'
    options = dict(corners=wp, start_date=dt.datetime(
        2003, 4, 1), stop_date=dt.datetime(2006, 3, 1))
    data_nc, var_nc, the_times, the_lats, the_lons, sst = get_var_2D(
        in_file, 'tos', **options)
    answer =\
        [[[301.8192138671875, 301.8794860839844, 301.97021484375],
          [301.93927001953125, 302.00830078125, 301.9566345214844],
            [302.3489074707031, 302.3004455566406, 302.2830810546875]],
            [[301.0838317871094, 301.2699279785156, 301.2352600097656],
             [301.2467956542969, 301.4319152832031, 301.5067443847656],
             [301.33978271484375, 301.5613708496094, 301.6506652832031]],
            [[301.1455993652344, 301.1784973144531, 301.1477355957031],
             [301.22052001953125, 301.2091369628906, 301.36724853515625],
             [301.5062255859375, 301.5807189941406, 301.6601257324219]]]
    #
    # We need to transform answer into a 3d ndarray so we can
    # compare to a slice using np.assert_allclose()
    # numpy can only initialize arrays from lists of lists (2d)
    # for 3d we need to flatten and reshape
    #
    flat1d = []
    for item2d in answer:
        [flat1d.extend(item) for item in item2d]
    answer = np.array(flat1d)
    answer = answer.reshape([3, 3, 3])

    result = sst[:3, :3, :3]
    nt.assert_allclose(result, answer)

if __name__ == "__main__":
    # https://nose.readthedocs.org/en/latest/usage.html
    # flags -vv verbose
    #      -s  don't capture stdout
    #      -x  stop after first error
    #      --pdb  drop into debugger
    #     --with-doctest  look for the doctest in find_index
    #     exit=False    keep running (needed to continue ipython
    #                   session
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb',
                         '--with-doctest'], exit=False)
