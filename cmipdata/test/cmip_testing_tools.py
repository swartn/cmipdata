"""
Tools used for testing the cmipdata package,
"""


import hashlib
import os
import cmipdata as cd
import cdo
cdo = cdo.Cdo()
from pyPdf import PdfFileWriter, PdfFileReader
    
def sha(ens):
    """ returns a dictionary linking the name of all
        the file in the ensemble and the SHA1# of
        those files
    Parameters
    ----------
    ens : Datanode
    
    Return
    ------
    dictionary of strings
    """        
    def hashfile(array):
        sha1 = hashlib.sha1(array)
        return sha1.hexdigest()
    data = {}
    for f in ens.objects('ncfile'):
         data[f.name] = hashfile(cdo.readMaArray(f.name, varname=f.parent.name))
    return data  

  
def loadtestfiles(directory, sourcefiles):
    """ Soft links the files into a directory for processing
    
    Parameters
    ----------
    directory : string
                the directory to link the files to
    sourcefiles : list
                  a list of the locations of the files to link
    """
    os.chdir(directory)
    os.system('rm -f *.nc')
    for f in sourcefiles:
        os.system('ln -s ' + f + ' .')
        
        
def print_dictionary_to_file(d,fi):
    """ Prints a dictionary to a file
    
    Parameters
    ----------
    d : dictionary
    fi : string
         name of the file to print the dictionary
    """
    with open(fi, 'w') as f:
        for key, value in d.items():
            f.write(key + '\t\t' + value + '\n')

def file_to_dictionary(fi):
    """returns a dictionary read from a file
    
    Parameters
    ----------
    fi : string
         name of the file to read
         
    Return
    ------
    dictionary
    """
    d = {}
    with open(fi) as f:
        for line in f:
            (key, val) = line.split()
            d[key] = val
    return d
            
def comparefiles(f1, f2):
    """ checks if the 2 string lines in a file are the same
       
    
    Parameters
    ----------
    f1, f2, : strings
              files to compare
    
    Return
    ------
    int is 0 if the files are the same
    """
    return cmp(file_to_dictionary(f1), file_to_dictionary(f2))  

def append_pdf(inp, out):
    """ adds the first page of a pdf file to a pdf writer
    
    Parameters
    ----------
    inp : string
          name of a pdf file
    out : pdfWriter()
    """
    out.addPage(inp.getPage(0))
