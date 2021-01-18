# AUTOGENERATED! DO NOT EDIT! File to edit: 01_features.ipynb (unless otherwise specified).

__all__ = ['read_tsv', 'gzip_reading', 'school_plan__features', 'translate_latlng', 'kdtree_neighbors',
           'train_plan__latlng', 'train_plan__nbusers', 'train_time_features', 'census_income_median',
           'census_income_avg', 'gini_processing', 'gini', 'census_sentiment_analy', 'convert_sent2score',
           'transform_churn_series', 'classifier']

# Cell
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

def school_plan__features(data:pd.DataFrame)->pd.DataFrame:
    'Calculate the number of school (and its associated types) within the planning area'
    school_count = data.groupby('planning_area', as_index=False).size().rename({'size':'number_school'}, axis=1)
    school_cat_count = (data
                        .groupby(['planning_area','category'], as_index=False).size()
                        .rename({'size':'number_school'}, axis=1)
                        .pivot(index='planning_area', columns='category', values='number_school').fillna(0)
                       ).reset_index()
    return school_count.merge(school_cat_count)

def translate_latlng(input:list)->list:
    'Translating the lat lng into tuple format, to be used to mathematically identify the nearest neighbor'
    latlong_location_str = [i.replace(" ","").replace("\"", "").split(",") for i in input]
    latlong_location_num = [(float(x), float(y)) for x, y in latlong_location_str]
    return latlong_location_num

def kdtree_neighbors(reference:list, query_data:list)->list:
    'Identify the nearest neighbor for *query_data*[list of (lat,lng)] to the *reference*[list of (lat,lng)], returning the matching reference index'
    tree = spatial.KDTree(reference)
    return tree.query(query_data)[1]

def train_plan__latlng(data:pd.DataFrame)->pd.DataFrame:
    list_tuple_latlng =  translate_latlng(data['latlong'])
    data['lat'] = [i[0] for i in list_tuple_latlng]
    data['lng'] = [i[1] for i in list_tuple_latlng]
    return data.groupby('planning_area', as_index=False)[['lat','lng']].median()

def train_plan__nbusers(data:pd.DataFrame)->pd.DataFrame:
    return data.groupby('planning_area', as_index=False).size().rename({'size':'users_nb'}, axis=1)

def train_time_features(data:pd.DataFrame):
    'Modify the train dataset inplace to generate time features (*month_delta* and *account start year*)'
    data['account_start_date'] = pd.to_datetime(data['account_start_date'])
    data['reference_date'] = pd.to_datetime(data['reference_date'])
    data['month_delta'] = [int(i/np.timedelta64(1, 'M')) for i in (data['reference_date'] - data['account_start_date'])]
    data['account_start_year'] = [i.year for i in data['account_start_date']]

def census_income_median(data:pd.DataFrame)->pd.DataFrame:
    'Calculate the median income and working pop for region excluding outliers (above 10K SGD and 0 SGD)'
    return (data
            .loc[~data['variable'].isin([12000,0])]
            .sort_values('value', ascending=False)
            .drop_duplicates(['planning_area'])
            .rename({'variable':'med_income','value':'working_pop'}, axis=1)
            .drop('working_pop', axis=1)
           )

def census_income_avg(data:pd.DataFrame)->pd.DataFrame:
    'Calculate average income based on the avg(pop * income)'
    return (census_income_dt_melt
            .assign(temp=census_income_dt_melt.eval('variable * value'))
             .groupby('planning_area')[['temp','value']]
             .sum()
             .eval('temp / value')
             .to_frame('avg_income')
             .reset_index()
            )

def gini_processing(census_perc_dt_melt:pd.DataFrame)->pd.DataFrame:
    'Parsing the income percent into np.array for gini calculation'
    income_per_dict = {'no_working_person_percent':0,
     'below_sgd_1000_percent':.05,
     'sgd_10000_over_percent':1,
     'sgd_1000_to_1999_percent':.15,
     'sgd_2000_to_2999_percent':.25,
     'sgd_3000_to_3999_percent':.35,
     'sgd_4000_to_4999_percent':.45,
     'sgd_5000_to_5999_percent':.55,
     'sgd_6000_to_6999_percent':.65,
     'sgd_7000_to_7999_percent':.75,
     'sgd_8000_to_8999_percent':.85,
     'sgd_9000_to_9999_percent':.95}

    census_perc_dt_melt['variable'] = census_perc_dt_melt['variable'].map(income_per_dict)
    census_perc_dt_melt.sort_values(['planning_area','variable'], inplace=True)
    census_perc_dt_melt = census_perc_dt_melt.assign(value = census_perc_dt_melt['value'].mul(10).astype(int))

    unique_areas = census_perc_dt_melt['planning_area'].unique()
    gini_dict={}
    for i in unique_areas: # looking at individual planning area seperately
        tmp_dt = census_perc_dt_melt.loc[census_perc_dt_melt['planning_area']==i][['variable','value']]
        tmp_list = [np.array([x]*y) for x, y in zip(tmp_dt['variable'], tmp_dt['value'])] # creation y records based on x value
        out = np.hstack(tmp_list).squeeze()
        gini_dict[i] = gini(out)

    gini_dt = pd.Series(gini_dict).to_frame().reset_index()
    gini_dt.columns = ['planning_area','gini_coef']
    return gini_dt

# adapted from https://github.com/oliviaguest/gini
def gini(array):
    'Calculate the Gini coefficient of a numpy array.'
    # based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
    # from: http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    array = array.flatten() #all values are treated equally, arrays must be 1d
    if np.amin(array) < 0:
        array -= np.amin(array) #values cannot be negative
    array += 0.0000001 #values cannot be 0
    array = np.sort(array) #values must be sorted
    index = np.arange(1,array.shape[0]+1) #index per array element
    n = array.shape[0]#number of array elements
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array))) #Gini coefficient


from transformers import pipeline
# Allocate a pipeline for sentiment-analysis
classifier = pipeline('sentiment-analysis')
def census_sentiment_analy(input:str)->tuple:
    output = classifier(input)
    return output

def convert_sent2score(input:dict):
    'Extract and convert the sentimental assignemnt to 0 (Negative), 0.5 (Neutral), 1 (Positive)'
    score_list=[]
    for i in input:
        if i['score'] > 0 and i['score'] < 0.7:
            score_list.append(0.5)
        elif i['label'] == 'POSITIVE':
            score_list.append(1.0)
        elif i['label'] == 'NEGATIVE':
            score_list.append(0.0)
    return score_list

def transform_churn_series(extracted_features_dt:pd.DataFrame, dt_churn:pd.DataFrame)->pd.DataFrame:
    'Extract churn data for significant test in x'
    churn_dt = dt_churn[['msisdn','churn']]

    churn_dt_ordered = (extracted_features_dt.reset_index()[['index']]
     .rename({'index':'msisdn'}, axis=1)
     .merge(churn_dt)
#      .drop(['voice_incoming__maximum'], axis=1)
     .set_index('msisdn')
    )

    return churn_dt_ordered