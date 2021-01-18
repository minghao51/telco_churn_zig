# AUTOGENERATED! DO NOT EDIT! File to edit: 00_exploration.ipynb (unless otherwise specified).

__all__ = ['read_tsv', 'gzip_reading']

# Cell
# Library
import pandas as pd
from zipfile import ZipFile
from scipy import spatial
import os

# Cell
# Functions
def read_tsv(file):
    return pd.read_csv(file,  compression='gzip', sep='\t')

def gzip_reading(gzip_file):
    archive = ZipFile(gzip_file, 'r')
    files = {name: archive.open(name) for name in archive.namelist() if
     (name.endswith('.gz') and not name.startswith('_'))}
    files_names = [i.split('.')[0] for i in files.keys()]

    dt={}
    for name, key in zip(files_names, files.keys()):
        dt[name]=read_tsv(files[key])

    return dt