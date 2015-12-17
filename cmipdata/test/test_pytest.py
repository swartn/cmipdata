"""
Runs the tests

"""
import os
import cmipdata as cd
import cmip_testing_tools as ctt
import cla as tc
import prept as tpt
import loa as tlt
cwd = os.getcwd()

# ------------------------------------------------------------------
# Configure
# ------------------------------------------------------------------
directory = '/home/004/david_fallis_sept2015/testprocessing/'
sourcefiles = ['/raid/ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CanESM2*rcp45*.nc',
               '/raid/ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CCSM4*historical*.nc',
               '/raid/ra40/CMIP5_OTHER_DOWNLOADS/ts/ts_Amon_CanESM2*historical*.nc']
variable = 'ts'
e1name = 'historical'
e2name = 'rcp45'
sd ='1950-01-01' 
ed ='2000-12-31'



def prepro(test, dataname, *args):
    data = test(*args)
    os.chdir(cwd + '/testdata')
    ctt.print_dictionary_to_file(data, dataname + '_data.txt')
    return ctt.comparefiles(dataname + '_data.txt', './sdata/standard_' + dataname + '_data.txt')

class TestInitialFiles:
    def test_initfile(self):
        assert prepro(tpt.test_starting_files, 'initialfiles', directory, sourcefiles) == 0    

class TestClasses:
    def testClasses(self):
        tc.test(directory, sourcefiles)

class TestPreprocessing:           
    def test_ces(self):
        assert prepro(tpt.test_cat_exp_slices, 'ces', directory, sourcefiles) == 0
    def test_ce(self):
        assert prepro(tpt.test_cat_experiments, 'ce', directory, sourcefiles, variable, e1name, e2name) == 0
    def test_zm(self):
        assert prepro(tpt.test_zonal_mean, 'zm', directory, sourcefiles) == 0
    def test_rmp(self):
        assert prepro(tpt.test_remap, 'rmp', directory, sourcefiles) == 0
    def test_ts(self):
        assert prepro(tpt.test_time_slice, 'ts', directory, sourcefiles, sd, ed) == 0
    def test_ta(self):    
        assert prepro(tpt.test_time_anomaly, 'ta', directory, sourcefiles, sd, ed) == 0  
    def test_mo(self):
       assert prepro(tpt.test_my_operator, 'mo', directory, sourcefiles, variable, e1name, e2name) == 0
    def test_ai(self):
        assert prepro(tpt.test_areaint, 'ai', directory, sourcefiles) == 0
    def test_am(self):    
        assert prepro(tpt.test_areamean, 'am', directory, sourcefiles) == 0
    def test_cmt(self):
        assert prepro(tpt.test_climatology, 'cmt', directory, sourcefiles) == 0
    """   
    es_data = tpt.test_ens_stats(directory, sourcefiles, variable)
    os.chdir(cwd + '/testdata')
    ctt.print_dictionary_to_file(es_data, 'es_data.txt')   
    """
class TestLoadingTools:
    def test_lf(self):
        assert prepro(tlt.test_loadingtools, 'tlt', directory, sourcefiles[2:], variable) == 0
           

