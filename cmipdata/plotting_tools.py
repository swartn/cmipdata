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
from matplotlib.backends.backend_pdf import PdfPages


def plot_realizations_1d(data, varname, dimension, ax=None, pdf="", png="",
                         xlabel="", ylabel="", title="",
                         kwargs={'color': [0.5, 0.5, 0.5]}):
    """ For each realization in ens (and data, which is generated from ens
    using loadfiles), plot the realization in color (grey by default)
    for variable varname. Data should be 1-d for each realization, along the
    dimension specified (time, lon, lat etc).
    
    Parameters
    ----------
    data : dictionary 
           returned from loadfiles()
           has keys 'data' and 'dimensions' which map to numpy arrays
    varname : str
              the name of the variable
    dimension : str
                variable for the x-axis
                ex. 'lat', 'time'
    ax : (optional) pyplot axis
    pdf : (optional) str
          name of file to save pdf
    png : (optional) str
          name of file to save png
    xlabel, ylabel, title : (optional) str
                            to label plot, could also be passed in kwargs
    kwargs : (optional) dict 
             options to pass to plt
             ex. {'color': [0.5, 0.5, 0.5]}
             
    EXAMPLES:
    # first call loadfiles to get the data dictionary
    data = cd.loadfiles(ens, 'tas', cdostr='-timmean -zonmean ')
    # plot the tas data against latitude in red
    cd.plot_realizations_1d(data, 'tas', dimension='lat', kwargs={'color':'r'})
    """
    plotdata = data["data"]
    dimensions = data["dimensions"]
    x = dimensions[dimension]

    if ax is None:
        ax = plt.gca()
        
    for r in range(plotdata.shape[0]):
        ax.plot(x, plotdata[r, :], **kwargs)

    if title == "":
        ax.set_title(varname)
    else:
        ax.set_title(title)

    if xlabel != "":
        plt.xlabel(xlabel)

    if ylabel != "":
        plt.ylabel(ylabel)

    if(png != ""):
        if not png.endswith('.png'):
            png = png + '.png'
        plt.savefig(png)

    if(pdf != ""):
        if pdf.endswith('.pdf'):
            pp = PdfPages(pdf)
        else:
            pdf = pdf + '.pdf'
            pp = PdfPages(pdf)
        plt.savefig(pp, format='pdf')
        pp.close()


def ensemble_envelope_timeseries(ens, meanfile, stdfile, varname, ax=None, pdf="", png="",
                                 kwargs={'linewidth': 3, 'color': 'k'}):
    """ For each realization in ens (and data, which is generated from ens
    using loadfiles), plot the realization in color (grey by default)
    for variable varname.
    
    Parameters
    ----------
    data : dictionary 
           returned from loadfiles()
           has keys 'data' and 'dimensions' which map to numpy arrays
    meanfile : str
               name of file with mean data, probably created by ens_stats()
    stdfile : str
              name of file with standard deviation data, probably created by ens_stats()
    varname : str
              the name of the variable

    ax : (optional) pyplot axis
    pdf : (optional) str
          name of file to save pdf
    png : (optional) str
          name of file to save png
    xlabel, ylabel, title : (optional) str
                            to label plot, could also be passed in kwargs
    kwargs : (optional) dict 
             options to pass to plt
             ex. {'color': [0.5, 0.5, 0.5]}

    EXAMPLES:
    # first call ens_stas to make the stats files
    cd. ens_stats(ens, 'ts')

    cd.plot_realizations_1d(data, 'ENS-MEAN_ts_Amon_CanESM2_historical_R-MEAN_195001-200012.nc', 
                            ENS-STD_ts_Amon_CanESM2_historical_STD_195001-200012.nc', 'ts', kwargs={'color':'r'})
    """

    dimensions = get_dimensions(meanfile, varname, toDatetime=True)
    time = dimensions['time']

    ens_mean = loadvar(meanfile, varname)
    ens_std = loadvar(stdfile, varname)

    if not ax:
        fig, ax = plt.subplots(1)

    num_models = len(list(ens.objects('model')))
    # the two-tailed 5% critical value from the t-dist
    c = sp.stats.t.isf(0.025, num_models - 1)
    # the 95% confidence interval
    ci95p = (c * ens_std) / np.sqrt(num_models)

    ax.fill_between(time, (ens_mean - ci95p), (ens_mean + ci95p),
                    color='k', alpha=0.25, edgecolor='none')
    ax.plot(time, ens_mean, **kwargs)
    plt.draw()

    if(png != ""):
        if not png.endswith('.png'):
            png = png + '.png'
        plt.savefig(png)

    if(pdf != ""):
        if pdf.endswith('.pdf'):
            pp = PdfPages(pdf)
        else:
            pdf = pdf + '.pdf'
            pp = PdfPages(pdf)
        plt.savefig(pp, format='pdf')
        pp.close()
    # ax.title(varname)
