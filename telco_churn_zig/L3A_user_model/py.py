# AUTOGENERATED! DO NOT EDIT! File to edit: 03A_churn_model.ipynb (unless otherwise specified).

__all__ = ['load_directory_files_dict']

# Cell
#exports

import pandas as pd
import numpy as np
import os


# Cell
from sklearn.ensemble import ExtraTreesClassifier, ExtraTreesRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Cell
def load_directory_files_dict(dir_path)->dict:
    'Load all pkl files in the directory into dict'
    L1file_list = os.listdir(path_load)
    L1file_list = [i for i in L1file_list if not i.startswith(".") and i.endswith('.pkl')]
    L1name_list = [i.split("_")[0]+"_"+i.split("_")[1].replace(".pkl","") for i in L1file_list]

    dt = {}
    for name, key in zip(L1file_list, L1name_list):
        dt[key] = pd.read_pickle(os.path.join(path_load,name))
    return dt