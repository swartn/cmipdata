"""plotting_tools
======================

The plotting_tools module of cmipdata is a set of functions which use 
matplotlib to produce various common plots.

The functions take an ensemble object and a data object. The ensemble
object is a cmipdata ensemble, the data object is a numpy array
generated using loading_tools.

**Note the plotting tools have not been fully developed, and are the lowest 
priority.**

  .. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>
"""
import matplotlib.pyplot as plt
from loading_tools import loadvar, get_dimensions
import scipy as sp
from scipy import stats
import numpy as np

def plot_realization_timeseries(ens, data, varname, kwargs={'color':[0.5, 0.5, 0.5]} ):
    """ For each realization in ens (and data, which is generated from ens
    using loadfiles), plot the realization in color (grey by default)
    for variable varname. kwargs is a dict of option to pass to plt,
    e.g.: kwargs={'color':'r'}
    """
    plot_realizations_1d(ens, data, varname, dimension='time', kwargs=kwargs)
  	
    
def plot_realizations_1d(ens, data, varname, dimension, kwargs={'color':[0.5, 0.5, 0.5]} ):
    """ For each realization in ens (and data, which is generated from ens
    using loadfiles), plot the realization in color (grey by default)
    for variable varname. Data should be 1-d for each realization, along the 
    dimension specified (time, lon, lat etc).
    
    kwargs is a dict of option to pass to plt,
    e.g.: kwargs={'color':'r'}
    
    EXAMPLES:
    
    # plot the uas data against latitude in red
    cd.plot_realizations_1d(ens, data, varname='uas', dimension='lat', kwargs={'color':'r'})
    """
    
    # First get the dimensions: A bad hack right now. Shouldn't reference attributes directly - use a function.
    v = ens.models[0].experiments[0].realizations[0].get_variable(varname)
    infile= v.filenames[0]
    dimensions = get_dimensions(infile, varname, toDatetime=True)
    x = dimensions[dimension]
    
    for r in range( data.shape[0] ):
	plt.plot( x, data[r,:], **kwargs)
	
    plt.title(varname)	
    
def ensemble_envelope_timeseries(ens, meanfile, stdfile, varname, ax='', kwargs={'linewidth':3, 'color':'k'}):
    """ For each realization in ens (and data, which is generated from ens
    using loadfiles), plot the realization in color (grey by default)
    for variable varname.
    """
    
    # First get the dimensions: A bad hack right now. Shouldn't reference attributes directly - use a function.
    dimensions = get_dimensions(meanfile, varname, toDatetime=True)
    time = dimensions['time']

    ens_mean = loadvar(meanfile, varname)
    ens_std = loadvar(stdfile, varname)
    
    if ax == '' :
	fig, ax = plt.subplots(1)
	
    num_models = ens.num_models()	
    c = sp.stats.t.isf(0.025, num_models - 1 )             # the two-tailed 5% critical value from the t-dist
    ci95p = ( c *  ens_std) / np.sqrt( num_models )     # the 95% confidence interval

    ax.fill_between(time, (ens_mean- ci95p), (ens_mean +  ci95p) , color='k', alpha=0.25,edgecolor='none' )
    ax.plot( time, ens_mean, **kwargs)
    plt.draw()
	
    #ax.title(varname)		