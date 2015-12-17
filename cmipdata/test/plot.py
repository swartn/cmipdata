"""
Tests of the plotting_tools module of cmipdata.

"""

import cmipdata as cd
import os
import cmip_testing_tools as ctt
import matplotlib.pyplot as plt
plt.ion()
from pyPdf import PdfFileWriter, PdfFileReader

def plotcompare(directory, cwd, plotname):
    """Combines the pdfs of the plot produced during testing and the standard stored in sdata
       to allow for visual comparison of the output. The pdf can be found in the /testdata/
       directory as {plotname}.pdf
    
    Parameters
    ----------
    directory : string
                directory where the data is being processed and the plot is found
    cwd : string
          directory of the test modules
    plotname : string
               name of the plot
    """
    output = PdfFileWriter()
    ctt.append_pdf(PdfFileReader(file(directory + plotname + '.pdf',"rb")),output)
    ctt.append_pdf(PdfFileReader(file(cwd + '/testdata/sdata/standard_' + plotname + '.pdf',"rb")),output)

    # Writing all the collected pages to a file
    output.write(file(cwd + '/testdata/' + plotname + '.pdf',"wb"))

def test_1dplot(directory, sourcefiles, var, cwd):
    """ Tests plot_realizations_1d for a non-timeseries plot
    
    Parameters
    ----------
    directory : string
                the directory to link the files to
    sourcefiles : list
                  a list of the locations of the files to link
    var : string
          the variable plotted
    cwd : string
          directory of the test modules
    """           
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    data = cd.loadfiles(ens, var, cdostr='-timmean -zonmean ')
    fig, axt = plt.subplots(1, 1, figsize=(8, 8))
    cd.plot_realizations_1d(data, var, 'lat', ax=axt, pdf='1dplot',
                        kwargs={'color': 'b', 'alpha': 0.3})
    plotcompare(directory, cwd, '1dplot')
    os.system('rm  1dplot.pdf')

                       
def test_1dtimeseries(directory, sourcefiles, var, cwd):
    """ Tests plot_realizations_1d for a timeseries plot
    
    Parameters
    ----------
    directory : string
                the directory to link the files to
    sourcefiles : list
                  a list of the locations of the files to link
    var :  string
           the variable plotted
    cwd : string 
          directory of the test modules
    """  
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    data = cd.loadfiles(ens, var, cdostr='-fldmean -yearmean', toDatetime=True)
    fig, axt = plt.subplots(1, 1, figsize=(8, 8))
    cd.plot_realizations_1d(data, var, 'time', ax=axt, pdf='tsplot',
                        kwargs={'color': 'r', 'alpha': 0.3})
    plotcompare(directory, cwd, 'tsplot')
    os.system('rm  tsplot.pdf') 
       
def test_ensembleenvelope(directory, sourcefiles, var, sd, ed, cwd):
    """ Tests ensemble_envelope_timeseries
    
    Parameters
    ----------
    directory : string
                the directory to link the files to
    sourcefiles : list
                  a list of the locations of the files to link
    var :  string
           the variable plotted
    sd : int
         start date for time slice
    ed : int
         end date for time slice
    cwd : string 
          directory of the test modules
    """
    ctt.loadtestfiles(directory, sourcefiles)
    filepattern = '*.nc'
    ens = cd.mkensemble(filepattern)
    ens = cd.time_slice(ens, sd, ed)
    ens = cd.remap(ens, 'r360x180', delete=True)
    ens = cd.my_operator(ens, my_cdo_str='cdo -fldmean -yearmean {infile} {outfile}', output_prefix='processed_', delete=True)
    cd.ens_stats(ens, var)
    cd.ensemble_envelope_timeseries(ens, 'ENS-MEAN_processed_remap_ts_Amon_CanESM2_historical_R-MEAN_195001-200012.nc', 'ENS-STD_processed_remap_ts_Amon_CanESM2_historical_STD_195001-200012.nc', var, pdf='ensenv')    
    plotcompare(directory, cwd, 'ensenv')
    os.system('rm  ensenv.pdf')               

