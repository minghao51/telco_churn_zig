# AUTOGENERATED! DO NOT EDIT! File to edit: 02B_geolocation_profile.ipynb (unless otherwise specified).

__all__ = ['imp_mean', 'imp_med', 'read_tsv', 'gzip_reading', 'load_directory_files_dict']

# Cell
#exports
import pandas as pd
import numpy as np
import os
from zipfile import ZipFile
from scipy import spatial
import matplotlib.pyplot as plt

from tsfresh import extract_features
from tsfresh.feature_selection.relevance import calculate_relevance_table
import tsfresh

# Cell
from sklearn.cluster import AgglomerativeClustering
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.inspection import plot_partial_dependence
from sklearn.impute import SimpleImputer

imp_mean = SimpleImputer(missing_values=np.nan, strategy='mean')
imp_med = SimpleImputer(missing_values=np.nan, strategy='median')

from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import balanced_accuracy_score, accuracy_score, classification_report
from sklearn.inspection import permutation_importance

from collections import defaultdict

# Cell
def read_tsv(file:str)->pd.DataFrame:
    return pd.read_csv(file,  compression='gzip', sep='\t')

def gzip_reading(gzip_file)->dict:
    'Read all tsv.gz files in the zip file and returning a dictionary (key:filename, value:data)'
    archive = ZipFile(gzip_file, 'r')
    files = {name: archive.open(name) for name in archive.namelist() if
     (name.endswith('.gz') and not name.startswith('_'))}
    files_names = [i.split('.')[0] for i in files.keys()]

    # reading the designated files into dict
    dt = {}
    for name, key in zip(files_names, files.keys()):
        dt[name] = read_tsv(files[key])
    return dt

def load_directory_files_dict(dir_path)->dict:
    'Load all pkl files in the directory into dict'
    L1file_list = os.listdir(path_load)
    L1file_list = [i for i in L1file_list if not i.startswith(".")]
    L1name_list = [i.split("_")[0]+"_"+i.split("_")[1].replace(".pkl","") for i in L1file_list]

    dt = {}
    for name, key in zip(L1file_list, L1name_list):
        dt[key] = pd.read_pickle(os.path.join(path_load,name))
    return dt