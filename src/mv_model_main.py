# Standard library imports
import json
import logging.config
import os
import sys
import time
import traceback

# Start logging temporarily with file object
sys.stderr = open('../logs/error.log', 'w')
info_log = open('../logs/info.log', 'w')
info_log.close()
date_format = time.strftime('%m/%d/%Y %H:%M:%S %p ')
sys.stderr.write(date_format + ' - root - [WARNING] - ')

# Third-party library imports
import numpy as np
import pandas as pd
import yaml

from sklearn import svm, cross_validation, linear_model, preprocessing, ensemble
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt

# Local imports
#  new modules - marco.pritoni@gmail.com
from data_preprocessor import DataPreprocessor
#from mv_script_marco import *
from PIPy_Datalink import pipy_datalink

def main():
    #TODO: Documentation
    #TODO: Caching to speed up

    start_logger()
    
    # Do not truncate numpy arrays when printing
    np.set_printoptions(threshold=np.nan)
        
    # Test example
    building_name = 'Ghausi'
    energy_type = 'ChilledWater'
    model_type = 'LinearRegression'
    base_start = '2014-01'
    base_end = '2014-12'    
    eval_start = '2015-01'
    eval_end = '2015-12'
    predict_start = '2016-01'
    predict_end = '2016-12'
    
           
    # Check if number of command-line arguments is correctly set
    if len(sys.argv) == 11:
        building_name = sys.argv[1]
        energy_type = sys.argv[2]
        model_type = 0
        base_start = sys.argv[3]
        base_end = sys.argv[4]
        base_start2 = sys.argv[5]
        base_end2 = sys.argv[6]
        eval_start = sys.argv[7]
        eval_end = sys.argv[8]
        predict_start = sys.argv[9]
        predict_end = sys.argv[10]
    
    else:
        logging.error("Incorrect number of command-line arguments!")
    
    # Time period to request data from PI system
    start = '2014'
    end = 't'
    
    data_name = '_'.join([building_name, energy_type, 'Demand_kBtu'])
    base_slice = (slice(base_start, base_end))
    eval_slice = (slice(eval_start, eval_end))
    predict_slice = (slice(predict_start, predict_end))
    
    downloader = pipy_datalink()
    data_raw = downloader.get_stream_by_point([data_name, 'OAT'], start, end)

    preprocessor = DataPreprocessor(data_raw)
    preprocessor.clean_data()
    preprocessor.add_degree_days(preprocessor.data_cleaned)
    preprocessor.add_time_features(preprocessor.data_preprocessed)
    preprocessor.create_dummies(preprocessor.data_preprocessed, var_to_expand=['TOD','DOW','MONTH'])
    data = preprocessor.data_preprocessed
    
    output_vars = [data_name]
    input_vars = ['hdh', 'cdh', u'TOD_0', u'TOD_1', u'TOD_2',
       u'TOD_3', u'TOD_4', u'TOD_5', u'TOD_6', u'TOD_7', u'TOD_8', u'TOD_9',
       u'TOD_10', u'TOD_11', u'TOD_12', u'TOD_13', u'TOD_14', u'TOD_15',
       u'TOD_16', u'TOD_17', u'TOD_18', u'TOD_19', u'TOD_20', u'TOD_21',
       u'TOD_22', u'TOD_23', u'DOW_0', u'DOW_1', u'DOW_2', u'DOW_3', u'DOW_4',
       u'DOW_5', u'DOW_6', u'MONTH_1', u'MONTH_2', u'MONTH_3', u'MONTH_4',
       u'MONTH_5', u'MONTH_6', u'MONTH_7', u'MONTH_8', u'MONTH_9', u'MONTH_10',
       u'MONTH_11', u'MONTH_12']
    
    data_set = DataSet(data, base_slice, base_slice, eval_slice, output_vars, input_vars)
    model = Model(model_type)
    model.train(data_set)
    model.output()
    #model.predict(data_set.eval_in.values)
    
    #model.output()
    '''
    # Old Simple Model
    # 1 filter data periods
    # 2 separate data-sets
    # 3 separate output and input
    
    training_data = np.array([data.loc[base_slice, data_name]])
    training_data = np.transpose(training_data)
    target_values = np.array([data.loc[base_slice, energy_type]])
    target_values = np.transpose(target_values)
    
    # 4 train a model
    clf = linear_model.LinearRegression()
    clf.fit(training_data, target_values)
    base_prediction = clf.predict(training_data)
    r2 = r2_score(target_values, base_prediction)
    print base_prediction
    print r2

    # 5 get scores for the model = validation
    
    eval_training_data = np.array([data.loc[eval_slice, data_name]])
    eval_training_data = np.transpose(eval_training_data)
    eval_target = np.array([data.loc[eval_slice, energy_type]])
    eval_target = np.transpose(eval_target)
    eval_predict = clf.predict(eval_training_data)
    r2 = r2_score(eval_target, eval_predict)
    print eval_predict
    print r2
    '''
    
    #Model variables
    '''
    out = [data_name]
    inp = ['hdh', 'cdh', u'TOD_0', u'TOD_1', u'TOD_2',
           u'TOD_3', u'TOD_4', u'TOD_5', u'TOD_6', u'TOD_7', u'TOD_8', u'TOD_9',
           u'TOD_10', u'TOD_11', u'TOD_12', u'TOD_13', u'TOD_14', u'TOD_15',
           u'TOD_16', u'TOD_17', u'TOD_18', u'TOD_19', u'TOD_20', u'TOD_21',
           u'TOD_22', u'TOD_23', u'DOW_0', u'DOW_1', u'DOW_2', u'DOW_3', u'DOW_4',
           u'DOW_5', u'DOW_6', u'MONTH_1', u'MONTH_2', u'MONTH_3', u'MONTH_4',
           u'MONTH_5', u'MONTH_6', u'MONTH_7', u'MONTH_8', u'MONTH_9', u'MONTH_10',
           u'MONTH_11', u'MONTH_12']
     
    clf = linear_model.LinearRegression()
    data_set = DataSet(data, base_slice, eval_slice, predict_slice, out, inp)
    model = clf.fit(data_set.bs1_in, data_set.bs1_out)
    score = model.score(data_set.eval_in.values, data_set.eval_out.values)
    
    output = data_set.bs2_out
    output["prediction"] = model.predict(data_set.bs2_in.values)
     
    print output.to_json()
    print(score)
    '''
    
    '''
    # 6 predict
    
    predict_training_data = np.array([data_cleaned.loc[predict_slice, data_name]])
    predict_training_data = np.transpose(predict_training_data)
    predict_target = np.array([data_cleaned.loc[predict_slice, energy_type]])
    predict_target = np.transpose(predict_target)
    extrapolated_data = clf.predict(predict_training_data)
    print extrapolated_data
    '''
    
'''Logging code'''
class StreamWriter():
    '''Custom logger to wrap around file streams'''
    
    def __init__(self, name = __name__):
        self.logger = logging.getLogger(name)
        
    def write(self, message):
        self.logger.warn(message)
        
        
class InfoFilter(logging.Filter):
    '''Filter to allow only INFO level messages to appear in info.log'''
    
    def __init__(self):
        super(InfoFilter, self).__init__('allow_info')
        
    def filter(self, record):
        if record.levelname == 'INFO':
            return 1
        return 0
                
                
def start_logger():   
    # Source: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
    default_path='logging.yaml'
    default_level=logging.INFO
    env_key='LOG_CFG'
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    
    sys.stderr.close()
    sys.stderr = StreamWriter()

'''Data'''
class DataSet(object):
    '''
    Inspired by Paul Raftery Class:
    fist prototype
    
    the dataset_type field is to help standardize notation of different datasets:
           'A':'measured pre-retrofit data',
           'B':'pre-retrofit prediction with pre-retrofit model',
           'C':'pre-retrofit prediction with post-retrofit model',
           'D':'measured post-retrofit data',
           'E':'post-retrofit prediction with pre-retrofit model',
           'F':'post-retrofit prediction with pos-tretrofit model',
           'G':'TMY prediction with pre-retrofit model',
           'H':'TMY prediction with post-retrofit model'
    typical comparisons used by mave:
        Pre-retrofit model performance = A vs B
        Single model M&V = D vs E
        Post retrofit model performance  = D vs F
        Dual model M&V, normalized to tmy data = G vs H
    '''
    
    def __init__(self, data, 
                 tPeriod1=(slice(None)),
                 tPeriod2=(slice(None)),
                 tPeriod3=(slice(None)),
                 out=[''],
                 inp=['']
                ):
        
        # the attributes dynamically calculated using indices and column names
        # first draft duplicates datasets
        #self.baseline1_par={'inpt':{'slicer':(slice(None)), 'col':['']},'outpt':{'slicer':(slice(None)), 'col':['']}}
        #self.baseline1_par={'inpt': {'col': ['OAT'], 'slicer':(slice(None))}, 'outpt': {'col': ['Ghausi_Electricity_Demand_kBtu'], 'slicer':(slice(None))}}
        
        self.fulldata=data
        try:
            self.bs1_in=data.loc[tPeriod1,inp]
        except:
            pass
        
        try:
            self.bs1_out=data.loc[tPeriod1,out]
        except:
            pass                   
                           
        try:
            self.bs2_in=data.loc[tPeriod2,inp]
        except:
            pass                   
        
        try:
            self.bs2_out=data.loc[tPeriod2,out]
        except:
            pass                   
        
        try:
            self.eval_in=data.loc[tPeriod3,inp]
        except:
            pass                   

        try:
            self.eval_out=data.loc[tPeriod3,out]
        except:
            pass                   
       

    def set_dataset(self, baseline_type, date_slicer, inpt, outpt):
        # need to develop a method to update stuff
        return
        
    def get_dataset(self, baseline_type, date_slicer, inpt_outpt):
        #ret=self.self.fulldata.loc[]
        
        return
    
class Model(object):    
    def __init__(self, model_type, data_set=None):
        self.clf = linear_model.LinearRegression()
        self.data_set = data_set
    
    def train(self, data_set):
        self.data_set = data_set
        self.clf.fit(data_set.bs1_in, data_set.bs1_out)
        data_set.bs1_out['Model'] = self.clf.predict(data_set.bs1_in.values)
        data_set.eval_out['Model'] = self.clf.predict(data_set.eval_in.values)
        out_var = self.data_set.eval_out.columns[0]
        #data_set.eval_out['Savings'] = data_set.eval_out['Model'].sub(data_set.eval_out[out_var])
        
    def predict(self, data):
        return self.clf.predict(data)
    
    # compare is a two column dataframe with one column with output variable and one with the model prediction
    # p is the number of variables in the model (eg. count the columns in the dataframe with input variables)
    @staticmethod
    def calc_scores(compare, p, out_var):
        scores={}
        
        n=compare.count()[1]
        R2=r2_score(compare[out_var], compare[["Model"]]) # this can be negative
        RMSE=((mean_squared_error(compare[out_var], compare[["Model"]]))*n/(n-p))**(0.5)
        CV_RMSE=RMSE*100/compare[out_var].mean()
        NMBE =(compare.diff(axis=1)[["Model"]]).sum()/(compare[["Model"]].mean())/(n-p)*100
        scores["Adj_R2"]= 1-(1-R2)*(n-1)/(n-p-1)
        scores["RMSE"]=RMSE
        scores["CV_RMSE"]=CV_RMSE
        scores["NMBE"]=NMBE
        return scores
    
    def output(self):
        num_inputs = len(self.data_set.bs1_in.columns)
        out_var = self.data_set.bs1_out.columns[0]
        print(self.data_set.bs1_out.to_json())
        print(self.data_set.eval_out.to_json())
        
        # TODO: Figure out how to serialize dict with numpy types
        # Likely fix: change data structure or serialize manually
        #print(json.dumps(self.calc_scores(self.data_set.bs1_out, num_inputs, out_var).tolist()))
        
        #print()
if __name__ == '__main__':
    try:
        main()
    except:
        # Logs and prints traceback
        logging.error(traceback.format_exc())
        sys.exit(1)
