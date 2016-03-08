"""
classes
=======

The classes module provides one classes and three functions.
The class: DataNode

The core functionality of :mod:`cmipdata` is to organize a large number of
model output files into a logical structure so that further processing
can be done. Data is organized into a tree-like structure using the class
DataNode as the nodes of a tree. The entire tree structure will be referred
to as an ensemble. At each level of the tree the level is specified by the
genre attribute.

Various methods exist to interact with the ensemble, and its
constituent elements.

The :func:`mkensemble` function is used to create :class:`Ensemble`
objects, while :func:`match_ensembles` finds models common to two ensembles and
:func:`match_reliazations` matches realizations between two ensembles. Once
created, an ensemble can be used to harness the power of
the :mod:`preprocessing_tools` to apply systematic operations to all files.

.. moduleauthor:: Neil Swart <neil.swart@ec.gc.ca>
"""

import os
import glob
import copy

class DataNode(object):
    """ Defines a cmipdata DataNode.

    Attributes
    ----------
    genre      : string
                 The attribute of DataNode
    name       : string
                 The name of the particular genre
    children   : list
                 List of DataNodees of genre beneath the current DataNode
    parent     : DataNode
                 for genre 'ensemble' the parent is None
    start_date : string
                 for genre 'file'
    end_date   : string
                 for genre 'file'
    realm      : string
                 for genre 'variable' contains the realm of the varaible

    """

    def __init__(self, genre, name, parent=None, **kwargs):
        """ Possible keys in kwargs:
                'start_date'
                'end_date'
                'realm'
        """
        self.genre = genre
        self.name = name
        self.children = []
        self.parent = parent
        for k,v in kwargs.items():
            setattr(self, k, v)

    def add(self, child):
        """ Add DataNode to children

        Parameters
        ----------
        child : DataNode
        """
        self.children.append(child)

    def delete(self, child):
        """Delete DataNode from children

        Parameters
        ----------
        child : DataNode
        """
        self.children.remove(child)

    def getNameWithoutDates(self):
        """ Return string name with the dates removed if present

        Returns
        -------
        string
        """
        return self.name.replace('_' + self.start_date + '-' + self.end_date + '.nc', "")

    def getChild(self, input_name):
        """ Returns DataNode given the name of the DataNode
            if it is in children

        Parameters
        ----------
        input_name : string

        Returns
        -------
        DataNode : Returns None if the DataNode is not in children
        """
        for child in self.children:
            if child.name == input_name:
                return child
        return None

    def mer(self):
        """Returns a generator containing lists of length 3
           with the DataNode genre:'realization'
                the DataNode genre:'experiment'
                string model-experiment-realization

        Returns
        -------
        generator
        """
        for obj in self.objects('realization'):
            yield [obj, obj.parent,
                   obj.parent.parent.name + '-' +
                   obj.parent.name + '-' +
                   obj.name]

    def lister(self, genre, unique=True):
        """ Returns a list of names of a particular genre

        Parameters
        ----------
        genre : string
                the genre of returned list
        unique: boolean
                if True removes duplicates from the list
        Return
        ------
        list of strings
        """
        def alist(item, genre):
            if item.genre == genre:
                yield item.name
            else:
                for child in item.children:
                    for value in alist(child, genre):
                        yield value
        if unique:
            return list(set(alist(self, genre)))
        else:
            return list(alist(self, genre))

    def objects(self, genre):
        """ Returns a generator for a DataNode of a particular genre

        Parameters
        ----------
        genre : string
                the genre of returned generator

        Return
        ------
        generator of DataNodees
        """
        def alist(item, genre):
            if item.genre == genre:
                yield item
            else:
                for child in item.children:
                    for value in alist(child, genre):
                        yield value
        return list(alist(self, genre))

    def parentobject(self, genre):
        """ Returns the parent DataNode of a particular genre

        Parameters
        ----------
        genre : string
                the genre of returned DataNode

        Return
        ------
        DataNode
        """
        def check(item):
            if item.genre == genre:
                return item
            else:
                return check(item.parent)
        return check(self)


    def _checkfile(self):
        """ Removes files from ensemble if they are not in the directory
        """
        for f in self.objects('ncfile'):
            if not os.path.isfile(f.name):
                f.parent.delete(f)         
         
        
        
    def squeeze(self):
        """ Remove any empty elements from the ensemble
        """
        self._checkfile()
        def sq(node):
            if node.children == [] and node.genre != 'ncfile':
                delete = node
                if node.genre != 'ensemble':
                    node = node.parent
                    node.delete(delete)
                    print 'Removing ' + delete.name + ' from ' + delete.parent.name
                    sq(node)
            for n in node.children:
                sq(n)
        for n in self.children:
            sq(n)

    def getDictionary(self):
        """Returns a dictionary which
           has the genres and their names for all the ancestors of
           the DataNode
        """
        node = self
        values = {}
        while node.genre != 'ensemble':
            values[node.genre] = node.name
            node = node.parent
        return values

    def sinfo(self, listOfGenres=['variable', 'model', 'experiment', 'realization', 'ncfile']):
        """ Returns the number of models, experiments, realizations, variables and files
        in the DataNode"""
        print "This ensemble contains:"
        for key in listOfGenres:
            if key == 'realization':
                print str(len(list(self.objects(key)))) + " " + key + "s"
            else:
                print str(len(self.lister(key))) + " " + key + "s"    
                  
    def fulldetails(self):
        """  prints information about the number of models,
             experiments, variables and files ina DataNode tree.
        """
        for model in self.children:
            print model.name + ':'
            for experiment in model.children:
                print '\t' + experiment.name
                for realization in experiment.children:
                    print '\t\t' + realization.name
                    for variable in realization.children:
                        print '\t\t\t' + variable.name
                        for filename in variable.children:
                            print '\t\t\t\t' + filename.name

    def fulldetails_tofile(self, fi):
        """  prints information about the number of models,
             experiments, variables and files ina DataNode tree.
        """
        with open(fi, 'w') as f:
            for model in self.children:
                f.write(model.name + ':\n')
                for experiment in model.children:
                    f.write('\t' + experiment.name + '\n')
                    for realization in experiment.children:
                        f.write('\t\t' + realization.name + '\n')
                        for variable in realization.children:
                            f.write('\t\t\t' + variable.name + '\n')
                            for filename in variable.children:
                                f.write('\t\t\t\t' + filename.name + '\n')

def mkensemble(filepattern, experiment='*', prefix='', kwargs=''):
    """Creates and returns a cmipdata ensemble from a list of
    filenames matching filepattern.

    Optionally specifying prefix will remove prefix from each filename
    before the parsing is done. This is useful, for example, to remove
    pre-pended paths used in filepattern (see example 2).

    Once the list of matching filenames is derived, the model, experiment,
    realization, variable, start_date and end_date fields are extracted by
    parsing the filnames against a specified file naming convention. By
    default this is the CMIP5 convention, which is::

        variable_realm_model_experiment_realization_startdate-enddate.nc

    If the default CMIP5 naming convention is not used by your files,
    an arbitary naming convention for the parsing may be specified by
    the dicionary kwargs (see example 3).


    Parameters
    ----------

    filepattern : string
                A string that by default is matched against all files in the
                current directory. But filepattern could include a full path
                to reference files not in the current directory, and can also
                include wildcards.

    prefix : string
             A pattern occuring in filepattern before the start of the official
             filename, as defined by the file naming converntion. For instance,
             a path preceeding the filename.

    EXAMPLES
    --------

    1. Create ensemble of all sea-level pressure files from the historical experiment in
    the current directory::

        ens = mkensemble('psl*historical*.nc')

    2. Create ensemble of all sea-level pressure files from all experiments in a non-local
    directory::

        ens = mkensemble('/home/ncs/ra40/cmip5/sam/c5_slp/psl*'
                      , prefix='/home/ncs/ra40/cmip5/sam/c5_slp/')

    3. Create ensemble defining a custom file naming convention::

        kwargs = {'separator':'_', 'variable':0, 'realm':1, 'model':2, 'experiment':3,
                  'realization':4, 'dates':5}

        ens = mkensemble('psl*.nc', **kwargs)

    """
    # find all files matching filepattern
    filenames = sorted(glob.glob(filepattern))

    if kwargs == '':
        kwargs = {'separator': '_', 'variable': 0, 'realm': 1, 'model': 2, 'experiment': 3,
                  'realization': 4, 'dates': 5}

    # Initialize the ensemble object
    ens = DataNode('ensemble', 'ensemble')

    # Loop over all files and
    for name in filenames:
        name = name.replace(prefix, '')
        variablename = name.split(kwargs['separator'])[kwargs['variable']]
        realm = name.split(kwargs['separator'])[kwargs['realm']]
        modelname = name.split(kwargs['separator'])[kwargs['model']]
        experiment = name.split(kwargs['separator'])[kwargs['experiment']]
        realization = name.split(kwargs['separator'])[kwargs['realization']]
        dates = name.split(kwargs['separator'])[kwargs['dates']]
        start_date = name.split(kwargs['separator'])[kwargs['dates']].split('-')[0]
        end_date = name.split(kwargs['separator'])[kwargs['dates']].split('-')[1].split('.')[0]

        # create the model if necessary
        m = ens.getChild(modelname)
        if m is None:
            m = DataNode('model', modelname, parent=ens)
            ens.add(m)

        # create the experiment if necessary
        e = m.getChild(experiment)
        if e is None:
            e = DataNode('experiment', experiment, parent=m)
            m.add(e)

        # create the realization if necessary
        r = e.getChild(realization)
        if r is None:
            r = DataNode('realization', realization, parent=e)
            e.add(r)

        # create the variable if necessary
        v = r.getChild(variablename)
        if v is None:
            v = DataNode('variable', variablename, parent=r, realm=realm)
            r.add(v)

        filename = (prefix + name)
        # create the file if necessary
        f = v.getChild(filename)
        if f is None:
            f = DataNode('ncfile', filename, parent=v, start_date=start_date, end_date=end_date)
            v.add(f)

    ens.sinfo()
    print('\n For more details use ens.fulldetails() \n')
    return ens


def match_models(ens1, ens2, delete=False):
    """
    Find common models between two ensembles.

    Parameters
    ----------
    ens1 : cmipdata ensemble
    ens2 : cmipdata ensemble
           the two cmipdata ensembles to compare.

    Returns
    -------
    ens1 : cmipdata ensemble
    ens2 : cmipdata ensemble
           two ensembles with matching models.

    """
    # get lists of the models in both ensembles
    ens1_modelnames = ens1.lister('model')
    ens2_modelnames = ens2.lister('model')

    # find the model misses
    model_misses = set(ens1_modelnames).symmetric_difference(ens2_modelnames)

    # remove the models that are not in both ensembles
    for name in model_misses:
        m = ens1.getChild(name)
        if m is not None:
            if delete:
                files = m.lister('ncfile')
                for f in files:
                    os.system('rm -f ' + f)
            print 'deleting %s from ens1' % (m.name)
            ens1.delete(m)

        m = ens2.getChild(name)
        if m is not None:
            if delete:
                files = m.lister('ncfile')
                for f in files:
                    os.system('rm -f ' + f)
            print 'deleting %s from ens2' % (m.name)
            ens2.delete(m)
    
    ens1.squeeze()
    ens2.squeeze()
    return ens1, ens2


def match_realizations(ens1, ens2, delete=False):
    """
    Find common realizations between two ensembles.

    Parameters
    ----------
    ens1 : cmipdata ensemble
    ens2 : cmipdata ensemble
           the two cmipdata ensembles to compare.

    Returns
    -------
    ens1 : cmipdata ensemble
    ens2 : cmipdata ensemble
           two ensembles with matching realizations.
    """
    
    mer_e1 = list(ens1.mer())
    mer_e2 = list(ens2.mer())

    # make lists of strings of form: model-experiment-realization
    mer_string_e1 = []
    mer_string_e2 = []
    for n in mer_e1:
        mer_string_e1.append(n[2])
    for n in mer_e2:
        mer_string_e2.append(n[2])

    # find matching and non-matching models
    matches = set(mer_string_e1).intersection(mer_string_e2)
    misses = set(mer_string_e1).symmetric_difference(mer_string_e2)

    print 'misses:', len(misses), 'matches:', len(matches)

    # delete realizations not in both ensembles
    def deleting(items):
        for nm in items:
            if nm[2] in misses:
                if delete:
                    files = nm[0].lister('ncfile')
                    for f in files:
                        os.system('rm -f ' + f) 
                nm[1].delete(nm[0])
    deleting(mer_e1)
    deleting(mer_e2)
    ens1.squeeze()
    ens2.squeeze()
    
    return ens1, ens2

if __name__ == "__main__":
    pass
