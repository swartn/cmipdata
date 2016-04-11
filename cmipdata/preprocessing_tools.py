"""preprocessing_tools
======================
 The preprocessing_tools module of cmipdata is a set of functions which use
 os.system calls to Climate Data Operators (cdo) to systematically apply a
 given processing on multiple NetCDF files, which are listed in cmipdata
 ensemble objects.

  .. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>
"""
import os
import glob
import classes as dc
import copy
import itertools

# ===========================================================================
# The next three operators work on multiple files across the ensemble,
# and cannot be chained together.
# ===========================================================================


def cat_exp_slices(ensemble, delete=True, output_prefix=''):
    """
    Concatenate multiple time-slice files per experiment.

    For all models in ens which divide their output into multiple files per
    experiment (time-slices), cat_exp_slices concatenates the files into one
    unified file, and deletes the individual slices, unless delete=False.
    The input ensemble can contain multiple models, experiments, realizations
    and variables, which cat_exp_slices will process independently. In other words,
    files are joined per-model, per-experiment, per-realization, per-variable.
    For example, if the ensemble contains two experiments for many models/realizations
    for variable psl, two unified files will be produced per realization: one for the
    historical and one for the rcp45 experiment. To join files
    over experiments (e.g. to concatenate historical and rcp45) see cat_experiments.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the concatenation.
    delete : boolean
             If delete=True, delete the individual time-slice files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          concatenated files.

    The concatenated files are written to present working directory.

    See also
    --------
    cat_experiments : Concatenate the files for two experiments.

    Examples
    ---------
    For a simple ensemble comprized of only 1 model, 1 experiment and one realization.::

      # Look at the ensemble structure before the concatenation
      ens.fulldetails()
      HadCM3:
          historical
                  r1i1p1
                          ts
                                ts_Amon_HadCM3_historical_r1i1p1_185912-188411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_188412-190911.nc
                                ts_Amon_HadCM3_historical_r1i1p1_190912-193411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_193412-195911.nc
                                ts_Amon_HadCM3_historical_r1i1p1_195912-198411.nc
                                ts_Amon_HadCM3_historical_r1i1p1_198412-200512.nc

      # Do the concantenation
      ens = cd.cat_exp_slices(ens)

      # Look at the ensemble structure after the concatenation
      ens.fulldetails()
      HadCM3:
          historical
                  r1i1p1
                          ts
                                ts_Amon_HadCM3_historical_r1i1p1_185912-200512.nc

    """
    ens = copy.deepcopy(ensemble)

    # Set the env variable to skip repeated times
    os.environ["SKIP_SAME_TIME"] = "1"
    
    # Loop over all variables
    for var in ens.objects('variable'):
        files = var.children
        modfiles = [f.name for f in files]
        startdates = [f.start_date for f in files]
        enddates = [f.end_date for f in files]
        # check if there are multiple files
        if len(modfiles) > 1:
            print 'joining files'
            infiles = ' '.join(modfiles)
            outfile = (output_prefix + 
                       os.path.split(files[0].getNameWithoutDates())[1] + '_' +
                       str(min(startdates)) + '-' +
                       str(max(enddates)) + '.nc')
            if not os.path.isfile(outfile):
                # join the files
                catstring = 'cdo mergetime ' + infiles + ' ' + outfile
                os.system(catstring)
            else:
                print outfile + ' already exists.'
            f = dc.DataNode('ncfile', outfile, parent=var, start_date=min(startdates), end_date=max(enddates))
            var.children = [f]

            # delete the old files
            if delete is True:
                for cfile in modfiles:
                    delstr = 'rm ' + cfile
                    os.system(delstr)
    ens.squeeze()
    return ens


def cat_experiments(ensemble, variable_name, exp1_name, exp2_name, delete=True, output_prefix=''):
    """Concatenate the files for two experiments.

    Experiments exp1 and exp2 are concatenated into a single file for each
    realization of each model listed in ens. For each realization, the concatenated file
    for variable variable_name is written to the current working directory and the input files
    are deleted by default, unless delete=False.

    The concatenation occurs for each realization for which input files
    exist for both exp1 and exp2.  If no match is found for the realization
    in exp1 (i.e. there is no corresponding realization in exp2), then the files
    for both experiments are deleted from the path (unless delete=False) and
    the realization is removed from ens. Similarly if exp2 is missing for a
    given model, that model is deleted from ens.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the concatenation.

    variable_name : str
                    The name of the variable to be concatenated.

    exp1_name : str
                    The name of the first experiment to be concatenated (e.g. 'historical').

    exp2_name : str
                    The name of the second experiment to be concatenated (e.g. 'rcp45').

    delete : boolean
             If delete=True, delete the individual time-slice files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          concatenated files.

          The concatenated files are written to present working directory.

    Examples
    ---------

    1. Join the historical and rcp45 simulations for variable ts in ens::

        ens = cd.cat_experiments(ens, 'ts', exp1_name='historical', exp2_name='rcp45')

    """
    ens = copy.deepcopy(ensemble)

    # Set the env variable to skip repeated times
    os.environ["SKIP_SAME_TIME"] = "1"

    # Create a copy of ens to use later for deleting input files if delete=True
    del_ens = copy.deepcopy(ens)

    # a list of models to remove from ens, if one experiment is missing
    # completely from the model
    models_to_delete = {}
    # a list of realizations to remove from ens, if the realization is missing
    # from one experiment
    realizations_to_delete = {}

    # Loop over all models
    for model in ens.children:
        e1 = model.getChild(exp1_name)
        e2 = model.getChild(exp2_name)
        
        for e in model.children:
            if e is not e1 and e is not e2:
                model.delete(e)

        # if the model is missing one experiment, remove that model from ens.
        if (e1 is not None) and (e2 is not None):
            # Get a list of realizations names in the two experiments.
            e1_r_names = [r.name for r in e1.children]
            e2_r_names = [r.name for r in e2.children]

            # Find matching realizations btwn the two experiments.
            realization_matches = set(e1_r_names).intersection(e2_r_names)
            realization_misses = set(e1_r_names).difference(e2_r_names)

            # add non-matching realizations to the realizations_deleted dict
            # for printing later
            if realization_misses:
                realizations_to_delete[model.name] = realization_misses

            # Delete non-matching realizations from ens, and do the join for
            # matching ones.
            for realization_name in realization_matches:
                # Get the realizations
                e1r = e1.getChild(realization_name)
                e2r = e2.getChild(realization_name)

                # Get the variable objects from the two experiments
                e1v = e1r.getChild(variable_name)
                e2v = e2r.getChild(variable_name)

                # join the two experiments original filenames with a whitespace
                filenames = []
                for f in e1v.children:
                    filenames.append(f.name)
                for f in e2v.children:
                    filenames.append(f.name)
                infiles = ' '.join(filenames)

                startdates = []
                enddates = []
                for f in e1v.children:
                    startdates.append(f.start_date)
                    enddates.append(f.end_date)
                for f in e2v.children:
                    startdates.append(f.start_date)
                    enddates.append(f.end_date)
                out_startdate = min(startdates)
                out_enddate = max(enddates)
                # construct the output filename
                outfile = (output_prefix + 
                           e1v.name + '_' + e1v.realm + '_' + model.name + '_' +
                           e1.name + '-' + e2.name + '_' +
                           e1r.name + '_' +
                           out_startdate + '-' +
                           out_enddate + '.nc')

                # do the concatenation using CDO
                print "\n join " + model.name + '_' + e1r.name + ' ' + e1.name + ' to ' + e2.name
                catstring = ('cdo mergetime ' + infiles + ' ' + outfile)

                os.system(catstring)

                # Add a new joined experiment to ens,
                # with a newly minted realization, variable + filenames.
                e = dc.DataNode('experiment', e1.name + '-' + e2.name, parent=model)
                model.add(e)

                r = dc.DataNode('realization', e1r.name, parent=e)
                e.add(r)

                v = dc.DataNode('variable', e1v.name, parent=r)
                r.add(v)
                f = dc.DataNode('ncfile', outfile, parent=v,
                                start_date=out_startdate,
                                end_date=out_enddate)
                v.add(f)

            # delete e1 and e2, which have been replaced with joined_e
            model.delete(e1)
            model.delete(e2)
        
        elif e1 is None and e2 is None:
            pass
        elif e2 is None:
            models_to_delete[model.name] = e1.name
        elif e1 is None:
            models_to_delete[model.name] = e2.name

    # If delete=True, delete the original files for variable_name,
    # leaving only the newly joined ones behind.
    if delete is True:
        for f in del_ens.objects('ncfile'):
            delstr = 'rm ' + f.name
            os.system(delstr)

    # Remove models with missing experiments from ens, and then return ens
    print ' \n\n Models deleted from ensemble (missing one experiment completely): \n'
    print '\t Model \t Experiment \n'

    for model_name, missing_experiment in models_to_delete.iteritems():
        ens.delete(ens.getChild(model_name))
        print '\t %s \t %s' % (model_name, missing_experiment)

    print ' \n\n Realizations deleted (missing from one experiment): \n'
    print '\t Model \t Realizations \n'
    for key, value in realizations_to_delete.iteritems():
        print '\t %s \t %s' % (key, ' '.join(value))

    ens.squeeze()
    return ens


def ens_stats(ens, variable_name, output_prefix=''):
    """ Compute the ensemble mean and standard deviation.

    The ensemble mean and standard deviation is computed over all models-realizations
    and experiments for variable variable_name in ens, such that each model has a weight
    of one. An output file is written containing the ensemble mean and another file is
    written with the standard deviation, containing the names '_ENS-MEAN_' and '_ENS-STD_'
    in the place of the model-name. If the ensemble contains multiple experiments, files
    are written for each experiment.

    The ensemble in ens must be homogenous. That is to say all files must be on the same
    grid and span the same time-frame, within each experiment (see remap, and time_slice for more).
    Additionally, variable_name should have only one filename per realization and experiment. That
    is, join_exp_slice should have been applied.

    The calculation is done by, first computing the mean over all realizations for each model;
    then for the ensemble, calculating the mean over all models.
    The standard deviation is calculated across models using the realization mean for each model.
     
    

        Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the concatenation.

    variable_name : str
                    The name of the variable to be concatenated.


    Returns
    -------
    A tuple of lists containing the names of the mean and standard deviation files created
    The ENS-MEAN and ENS-STD files are written to present working directory.

    Examples
    ---------

    1. Compute the statistics for the ts variable::

        >>cd.ens_stats(ens, 'ts')



    experiment_list = ens.lister('experiment')
    for exname in experiment_list:
        files_to_mean = []
        for model in ens.objects('model'):
            experiment = model.getChild(exname)
            if experiment != None:
                modfilesall = []
                for realization in experiment.children:
                    realization
                    modfilesall.append(realization.getChild(variable_name).children)
    """
    meanfiles = []
    stdevfiles = []
    experiments = {}
    for f in ens.objects('ncfile'):
        table = f.getDictionary()
        if table['variable'] == variable_name:
            if table['experiment'] in experiments:
                experiments[table['experiment']].append([f, table['model']])
            else:
                experiments[table['experiment']] = [[f, table['model']]]
    # multiple output files for multiple experiments
    for experimentname in experiments:
        files_to_mean = []
        models = {}
        for fm in experiments[experimentname]:
            if fm[1] in models:
                models[fm[1]].append(fm[0])
            else:
                models[fm[1]] = [fm[0]]
        for model in models:
            files = models[model]

            fnames = []
            for f in files:
                fnames.append(f.name)

            inputfiles = ''
            for f in fnames:
                inputfiles = inputfiles + ' ' + f
            outfile = output_prefix + os.path.split(fnames[0])[1].replace(files[0].parent.parent.name, 'R-MEAN')
            cdostr = 'cdo ensmean ' + inputfiles + ' ' + outfile

            if os.path.isfile(outfile):
                files_to_mean.append(outfile)
            else:
                os.system(cdostr)
                files_to_mean.append(outfile)

        in_files = ' '.join(files_to_mean)
        print files_to_mean[0]
        print experiments[experimentname][0][1]
        outfilename = os.path.split(files_to_mean[0])[1].replace(experiments[experimentname][0][1] + '_', "")
        print outfilename
        out_file = output_prefix + 'ENS-MEAN_' + outfilename

        cdo_str = 'cdo ensmean ' + in_files + ' ' + out_file
        os.system(cdo_str)
        meanfiles.append(out_file)

        # Now do the standard deviation
        out_file = output_prefix + 'ENS-STD_' + outfilename.replace('R-MEAN', 'STD')

        cdo_str = 'cdo ensstd ' + in_files + ' ' + out_file
        os.system(cdo_str)
        stdevfiles.append(out_file)

        for fname in files_to_mean:
            os.system('rm ' + fname)
    return meanfiles, stdevfiles

# =========================================================================
# The operators below this point work on a file-by-file basis and can be chained together
# (in principle, not implemented). Practically my_operator can be used to chain operations.
# =========================================================================


def areaint(ensemble, delete=True, output_prefix=''):
    """
    Calculate the area weighted integral for each file in ens.

    The output files are prepended with 'area-integral'. The original
    the input files are removed  if delete=True (default). An updated
    ensemble object is also returned.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.

    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory.

    Examples
    --------

    1. Compute the area integral for all files in ens::

        ens = cd.areaint(ens)

    """
    ens = copy.deepcopy(ensemble)
    
    # loop over all files
    for f in ens.objects('ncfile'):
        outfile = output_prefix + 'area-integral_' + os.path.split(f.name)[1]

        cdostr = 'cdo fldsum -mul ' + f.name + ' -gridarea ' + f.name + ' ' + outfile
        os.system(cdostr)
        
        # delete old files
        if delete is True:
            delstr = 'rm ' + f.name
            os.system(delstr)

        var = f.parent
        ncfile = dc.DataNode('ncfile', outfile, parent=var, start_date=f.start_date, end_date=f.end_date)
        var.add(ncfile)
        var.delete(f)

    return ens


def areamean(ensemble, delete=True, output_prefix=''):
    """
    Calculate the area mean for each file in ens.

    The output files are prepended with 'area-mean'. The original
    the input files are removed  if delete=True (default). An updated
    ensemble object is also returned.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.

    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory.

    Examples
    --------

    1. Compute the area mean for all files in ens::

        area_mean_ens = cd.areamean(ens)

    """
    ens = copy.deepcopy(ensemble)
    
    # loop over all files
    for f in ens.objects('ncfile'):
        outfile = output_prefix + 'area-mean_' + os.path.split(f.name)[1]

        cdostr = 'cdo fldmean ' + f.name + ' ' + outfile
        os.system(cdostr)
        
        # delete old files
        if delete is True:
            delstr = 'rm ' + f.name
            os.system(delstr)

        var = f.parent
        ncfile = dc.DataNode('ncfile', outfile, parent=var, start_date=f.start_date, end_date=f.end_date)
        var.add(ncfile)
        var.delete(f)

    return ens


def zonmean(ensemble, delete=True, output_prefix=''):
    """
    Calculate the zonal mean for each file in ens.

    The output files are prepended with 'zonal-mean'. The original
    the input files are removed  if delete=True (default). An updated
    ensemble object is also returned.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.

    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory.

    Examples
    ---------

    1. Compute the zonal mean for all files in ens::

        zonal_mean_ens = cd.zonmean(ens)

    """
    ens = copy.deepcopy(ensemble)
    
    # loop over all files
    for f in ens.objects('ncfile'):
        outfile = output_prefix + 'zonal-mean_' + os.path.split(f.name)[1]

        cdostr = 'cdo zonmean ' + f.name + ' ' + outfile
        ex = os.system(cdostr)

        var = f.parent
        
        # if zonalmean is not succesful, delete the new file
        if ex != 0:
            try:
                print 'deleting ' + outfile
                os.system('rm -f ' + outfile)
            except:
                pass
        else:
            ncfile = dc.DataNode('ncfile', outfile, parent=var, start_date=f.start_date, end_date=f.end_date)
            var.add(ncfile)

        var.delete(f)
        
        # delete the old files
        if delete is True:
            delstr = 'rm ' + f.name
            os.system(delstr)

    return ens


def climatology(ensemble, delete=True, output_prefix=''):
    """
    Compute the monthly climatology for each file in ens.

    The climatology is calculated over the full file-length using
    cdo ymonmean, and the output files are prepended with 'climatology_'.
    The original the input files are removed  if delete=True (default).
    An updated ensemble object is also returned.

    If you want to compute the climatology over a specific time slice, use time_slice
    before compute the climatology.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the remapping.

    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory.

    Examples
    --------

    1. Compute the climatology::

        climatology_ens = cd.climatology(ens)

    """
    ens = copy.deepcopy(ensemble)
    
    # loop over all the files
    for f in ens.objects('ncfile'):
        outfile = output_prefix + 'climatology_' + os.path.split(f.name)[1]
        var = f.parent
        cdostr = 'cdo ymonmean -selvar,' + var.name + ' ' + f.name + ' ' + outfile
        os.system(cdostr)
        
        # delete the old file
        if delete is True:
            delstr = 'rm ' + f.name
            os.system(delstr)

        ncfile = dc.DataNode('ncfile', outfile, parent=var, start_date=f.start_date, end_date=f.end_date)
        var.add(ncfile)
        var.delete(f)

    return ens


def remap(ensemble, remap='r360x180', method='remapdis', delete=True, output_prefix=''):
    """
    Remap files to a specified resolution.

    For each file in ens, remap to resolution remap='r_nlon_x_nlat_', where _nlon_,
    _nlat_ are the number of lat-lon points to use. Removal of the original input
    files occurs if delete=True (default). An updated ensemble object is also returned.

    By default the distance weighted remapping is used, but any valid cdo
    remapping method can be used by specifying the option argument 'method',
    e.g. method='remapdis'.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the remapping.

    remap : str
          The resolution to remap to, e.g. for a 1-degree grid remap='r360x180'

    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory.


    EXAMPLE:
    --------

    1. remap files to a one-degree grid::

        ens = cd.remap(ens, remap='r1x180')

    """

    ens = copy.deepcopy(ensemble)
    
    # loop over all files
    for f in ens.objects('ncfile'):
        outfile = output_prefix + 'remap_' + os.path.split(f.name)[1]
        var = f.parent
        cdostr = ('cdo ' + method + ',' + remap + ' -selvar,' +
                  var.name + ' ' + f.name + ' ' + outfile)
        ex = os.system(cdostr)
        
        # if remapping is not successful delete the new file
        if ex != 0:
            try:
                print 'deleting ' + outfile
                os.system('rm -f ' + outfile)
            except:
                pass
        else:
            ncfile = dc.DataNode('ncfile', outfile, parent=var, start_date=f.start_date, end_date=f.end_date)
            var.add(ncfile)

        var.delete(f)

        # delete the old file
        if delete is True:
            delstr = 'rm ' + f.name
            os.system(delstr)

    return ens


def time_slice(ensemble, start_date, end_date, delete=True, output_prefix=''):
    """
    Limit the data to the period between start_date and end_date,
    for each file in ens.

    The resulting output is written to file, named with with the correct
    date range, and the original input files are deleted if delete=True.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.

    start_date : str
                 Start date for the output file with format: YYYY-MM-DD
    end_date : str
                 End date for the output file with format: YYYY-MM-DD

    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory.


    EXAMPLES
    ---------
    1. Select data between 1 January 1980 and 31 December 2013::

        ens = cd.time_slice(ens, start_date='1979-01-01', end_date='2013-12-31')

    """
    ens = copy.deepcopy(ensemble)
    date_range = start_date + ',' + end_date

    # convert dates to CMIP YYYYMM format
    start_yyyymm = start_date.replace('-', '')[0:6]
    end_yyyymm = end_date.replace('-', '')[0:6]

    for f in ens.objects('ncfile'):
        print f.name
        # don't proceed if the file already has the correct start date
        if f.start_date != start_yyyymm or f.start_date != end_yyyymm:
            var = f.parent
            # check that the new date range is within the old date range
            if f.start_date <= start_yyyymm and f.end_date >= end_yyyymm:
                outfile = output_prefix + os.path.split(f.getNameWithoutDates())[1] + '_' + start_yyyymm + '-' + end_yyyymm + '.nc'
                print 'time limiting...'

                cdostr = ('cdo -L seldate,' + date_range + ' -selvar,' +
                          var.name + ' ' + f.name + ' ' + outfile)
                ex = os.system(cdostr)

                # if the time silcing is unsuccesful, remove the new file
                if ex != 0:
                    try:
                        print 'deleting ' + outfile
                        os.system('rm -f ' + outfile)
                    except:
                        pass
                else:
                    ncfile = dc.DataNode('ncfile', outfile, parent=var,
                                         start_date=start_yyyymm, end_date=end_yyyymm)
                    var.add(ncfile)

            else:
                print "%s %s is not in the date-range" % (var.parent.parent.parent.name, var.parent.name)

            var.delete(f)
            
            # delete the old file
            if delete is True:
                delstr = 'rm ' + f.name
                os.system(delstr)
    ens.squeeze()
    return ens


def time_anomaly(ensemble, start_date, end_date, delete=False, output_prefix=''):
    """
    Compute the anomaly relative the period between start_date and end_date,
    for each file in ens.

    The resulting output is written to file with the prefix 'anomaly_', and the
    original input files are deleted if delete=True.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.

    start_date : str
                 Start date for the base period with format: YYYY-MM-DD
    end_date : str
                 End date for the base period with format: YYYY-MM-DD


    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory.


    EXAMPLES
    ---------

    1. Compute the anomaly relative to the base period 1980 to 2010::

        ens = cd.time_anomaly(ens, start_date='1980-01-01', end_date='2010-12-31')

    """
    ens = copy.deepcopy(ensemble)
    date_range = start_date + ',' + end_date

    # convert dates to CMIP YYYYMM format
    start_yyyymm = start_date.replace('-', '')[0:6]
    end_yyyymm = end_date.replace('-', '')[0:6]
    # loop over all files
    for f in ens.objects('ncfile'):
        var = f.parent
        # check the date range is within the file date range
        if f.start_date <= start_yyyymm and f.end_date >= start_yyyymm:
            var = f.parent
            outfile = output_prefix + 'anomaly_' + os.path.split(f.name)[1]
            cdostr = ('cdo sub ' + f.name + ' -timmean -seldate,' + date_range +
                      ' -selvar,' + var.name + ' ' + f.name + ' ' + outfile)
            os.system(cdostr)

            ncfile = dc.DataNode('ncfile', outfile, parent=var, start_date=f.start_date, end_date=f.end_date)
            var.add(ncfile)
        var.delete(f)

        # delete the old file
        if delete is True:
            delstr = 'rm ' + f.name
            os.system(delstr)
    ens.squeeze()
    return ens


def my_operator(ensemble, my_cdo_str="", output_prefix='processed_', delete=False):
    """
    Apply a customized cdo operation to all files in ens.

    For each file in ens the command in my_cdo_str is applied and an output
    file appended by 'output_prefix' is created.

    Optionally delete the original input files if delete=True.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.

    my_cdo_str : str
                 The (chain) of cdo commands to apply. Defined variables which can
                 be used in my_cdo_str are: model, experiment, realization, variable,
                 infile, outfile

    output_prefix : str
                 The string to prepend to the processed filenames.

    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory.


    EXAMPLES
    ---------

    1. Do an annual mean::

           my_cdo_str = 'cdo -yearmean {infile} {outfile}'
           my_ens = cd.my_operator(ens, my_cdo_str, output_prefix='annual_')

    2. Do a date selection and time mean::

           my_cdo_str = 'cdo sub {infile} -timmean -seldate,1991-01-01,2000-12-31 {infile} {outfile}'
           my_ens = cd.my_operator(ens, my_cdo_str, output_prefix='test_')

    """
    ensem = copy.deepcopy(ensemble)
    if delete is True:
        # Take a copy of the original ensemble before we modify it below
        del_ens = copy.deepcopy(ensemble)
    
    # loop over all files
    for f in ensem.objects('ncfile'):
        outfile = output_prefix + os.path.split(f.name)[1]
        values = f.getDictionary()
        values['infile'] = f.name
        values['outfile'] = outfile
        cdostr = my_cdo_str.format(**values)
        ex = os.system(cdostr)
        var = f.parent
        
        # if the operation is unsuccessful, delete the new file
        if ex != 0:
            try:
                print 'Failed processing... deleting ' + outfile
                os.system('rm -f ' + outfile)
            except:
                pass
        else:
            ncfile = dc.DataNode('ncfile', outfile, parent=var, start_date=f.start_date, end_date=f.end_date)
            var.add(ncfile)
        var.delete(f)

    if delete is True:
        del_ens_files(del_ens)

    ensem.squeeze()
    return ensem


def del_ens_files(ensem):
    """ delete from disk all files listed in ensemble ens"""
    for infile in ensem.objects('ncfile'):
        delstr = 'rm ' + infile.name
        os.system(delstr)
        infile.parent.delete(infile)
    ensem.squeeze()


def trends(ensemble, start_date, end_date, delete=False):
    """
    Compute linear trends over the period between start_date and end_date,
    for each file in ens.

    The resulting output is written to file, named with with the correct
    date range, and the original input files are deleted if delete=True.

    Parameters
    ----------
    ens : cmipdata Ensemble
          The ensemble on which to do the processing.

    start_date : str
                 Start date for the output file with format: YYYY-MM-DD
    end_date : str
                 End date for the output file with format: YYYY-MM-DD

    delete : boolean
             If delete=True, delete the original input files.

    Returns
    -------
    ens : cmipdata Ensemble
          An updated ensemble object, containing the names of the newly
          processed files.

    The processed files are also written to present working directory,
    and begin with "slope_" and "intercept_".


    EXAMPLES
    ---------
    1. Select data between 1 January 1980 and 31 December 2013::

        ens = cd.trends(ens, start_date='1979-01-01', end_date='2013-12-31')

    """

    # copy the ens object
    ens = copy.deepcopy(ensemble)

    # set up the dates in cmip5 format
    date_range = start_date + ',' + end_date
    start_yyyymm = start_date.replace('-', '')[0:6]  # convert date format
    end_yyyymm = end_date.replace('-', '')[0:6]

    # loop over all files
    for f in ens.objects('ncfile'):
        var = f.parent
        # check the date range is within the file range
        if f.start_date <= start_yyyymm and f.end_date >= end_yyyymm:
            outfile = f.getNameWithoutDates() + '_' + start_yyyymm + '-' + end_yyyymm + '.nc'
            print 'time limiting...'
            cdostr = ('cdo trend -seldate,' + date_range + ' ' +
                      '-selvar,' + var.name + ' ' + f.name + ' ' +
                      'intercept_' + outfile + ' ' +
                      'slope_' + outfile)

            ex = os.system(cdostr)
            
            # if the trands are not successful the new file is deleted
            if ex != 0:
                try:
                    print 'Failed processing... deleting ' + outfile
                    os.system('rm -f ' + outfile)
                    os.system('rm -f intercept_' + outfile)
                    os.system('rm -f slope_' + outfile)
                except:
                    pass
            else:
                ncfile = dc.DataNode('ncfile', outfile, parent=var, start_date=start_yyyymm, end_date=end_yyyymm)
                var.add(ncfile)
                ncfile = dc.DataNode('ncfile', 'intercept_' + outfile, parent=var, start_date=start_yyyymm, end_date=end_yyyymm)
                var.add(ncfile)
                ncfile = dc.DataNode('ncfile', 'slope_' + outfile, parent=var, start_date=start_yyyymm, end_date=end_yyyymm)
                var.add(ncfile)
        var.delete(f)
        
        # delete the old file
        if delete is True:
            delstr = 'rm ' + f.name
            os.system(delstr)

    return ens
