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
    model.savings(data_set)
    
    print(data_set.bs1_out.to_json())
    print(data_set.eval_out.to_json())
    
    '''
    # 6 predict
    
    predict_training_data = np.array([data_cleaned.loc[predict_slice, data_name]])
    predict_training_data = np.transpose(predict_training_data)
    predict_target = np.array([data_cleaned.loc[predict_slice, energy_type]])
    predict_target = np.transpose(predict_target)
    extrapolated_data = clf.predict(predict_training_data)
    print extrapolated_data
    '''
    # 7 compare    
    #data = data_preprocessor.feature_extraction(data_cleaned)
    
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
    def __init__(self, model_type):
        self.clf = linear_model.LinearRegression()
    
    def train(self, data_set):
        self.clf.fit(data_set.bs1_in, data_set.bs1_out)
        data_set.bs1_out["prediction"] = self.clf.predict(data_set.bs1_in.values);
        data_set.eval_out["prediction"] = self.clf.predict(data_set.eval_in.values);
        print self.clf.score(data_set.bs1_in.values, data_set.bs1_out.values);
        
    def predict(self, data):
        return self.clf.predict(data)

    #calculate savings. 
    def savings(self, data_set):
        #not sure what the difference between bs1_out and bs1_in is
        data_set.bs1_out["savings"] = data_set.bs1_in.values - data_set.eval_in.values
        print data_set.bs1_out["savings"]
    
    #def output(self):
    #    print output.to_json()
    #    print(score)
    
if __name__ == '__main__':
    try:
        main()
    except:
        # Logs and prints traceback
        logging.error(traceback.format_exc())
        sys.exit(1)
