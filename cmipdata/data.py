class cmipdata(object):

    def __init__(self, filename, variablename, modelname, realization, experiment, start_year, end_year):
        self.filename     = filename
        self.variablename = variablename
        self.modelname    = modelname
        self.realization  = realization
        self.experiment   = experiment
        self.start_year   = start_year
        self.end_year     = end_year
    
    def __str__(self):
        return "cmipdata object for %s" % (self.modelname)