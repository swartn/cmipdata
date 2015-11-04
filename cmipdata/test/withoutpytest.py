"""
Runs the tests without pytest

"""
import os
import cmipdata as cd
import cmip_testing_tools as ctt
import cla as tc
import prept as tpt
import loa as tlt
import plot as plo
cwd = os.getcwd()
from pyPdf import PdfFileWriter, PdfFileReader
import time

def prepro(test, dataname, *args):
    t0 = time.clock()
    data = test(*args)
    os.chdir(cwd + '/testdata')
    ctt.print_dictionary_to_file(data, dataname + '_data.txt')
    with open('testresults.txt', 'a') as f:
        if ctt.comparefiles(dataname + '_data.txt', './sdata/standard_' + dataname + '_data.txt') == 0:
            f.write(dataname + ' Passed   Time: ' + str(time.clock()-t0) + '(sec)\n')
            print dataname + ' Passed'
        else:
            f.write(dataname + ' Failed\n')
            print dataname + ' Failed'
   

def testStartingFiles(directory, sourcefiles):
    prepro(tpt.test_starting_files, 'initialfiles', directory, sourcefiles)
    
        
def testClasses(directory, sourcefiles):
    tc.test(directory, sourcefiles, cwd)

           
def testPreprocessing(directory, sourcefiles, variable, e1name, e2name, sd, ed):
    prepro(tpt.test_cat_exp_slices, 'ces', directory, sourcefiles)
    prepro(tpt.test_cat_experiments, 'ce', directory, sourcefiles, variable, e1name, e2name)
    prepro(tpt.test_zonal_mean, 'zm', directory, sourcefiles)
    prepro(tpt.test_remap, 'rmp', directory, sourcefiles)
    prepro(tpt.test_time_slice, 'ts', directory, sourcefiles, sd, ed)
    prepro(tpt.test_time_anomaly, 'ta', directory, sourcefiles, sd, ed)   
    prepro(tpt.test_my_operator, 'mo', directory, sourcefiles, variable, e1name, e2name)
    prepro(tpt.test_areaint, 'ai', directory, sourcefiles)
    prepro(tpt.test_areamean, 'am', directory, sourcefiles)
    prepro(tpt.test_climatology, 'cmt', directory, sourcefiles)
    """   
    es_data = tpt.test_ens_stats(directory, sourcefiles, variable)
    os.chdir(cwd + '/testdata')
    ctt.print_dictionary_to_file(es_data, 'es_data.txt')   
    """   

def testLoadingTools(directory, sourcefiles, variable):
    prepro(tlt.test_loadingtools, 'tlt', directory, sourcefiles[2:], variable)
    
    

def testPlottingTools(directory, sourcefiles, variable):
    plo.test_1dplot(directory, sourcefiles[-1:], variable, cwd)
    plo.test_1dtimeseries(directory, sourcefiles[-1:], variable, cwd)  
    plo.test_ensembleenvelope(directory, sourcefiles[-2:], variable, start_date, end_date, cwd)
             
if __name__ == "__main__":
    directory = '/home/004/david_fallis_sept2015/testprocessing/'
    sourcefiles = ['/raid/ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CanESM2*rcp45*.nc',
                   '/raid/ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CCSM4*historical*.nc',
                   '/raid/ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CanESM2*historical*.nc']
    plotfiles = []
    variable = 'ts'
    expr1name = 'historical'
    expr2name = 'rcp45'
    start_date='1950-01-01' 
    end_date='2000-12-31'
    
    open('./testdata/testresults.txt', 'w').close()
    testStartingFiles(directory, sourcefiles)
    testClasses(directory, sourcefiles)
    testPreprocessing(directory, sourcefiles, variable, expr1name, expr2name, start_date, end_date)
    testLoadingTools(directory, sourcefiles, variable)
    testPlottingTools(directory, sourcefiles, variable)
