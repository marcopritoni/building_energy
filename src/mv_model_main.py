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

# Local imports
#  new modules - marco.pritoni@gmail.com
from data_preprocessor import DataPreprocessor
#from mv_script_marco import *
from PIPy_Datalink import pipy_datalink

def main():
    #TODO: Documentation of this function
    #TODO: Caching to speed up
    
    '''
    building_name = sys.argv[1]
    energy_type = sys.argv[2]
    start = sys.argv[3]
    end = sys.argv[4]
    base_start = sys.argv[5]
    base_end = sys.argv[6]
    eval_start = sys.argv[7]
    eval_end = sys.argv[8]
    predict_start = sys.argv[9]
    predict_end = sys.argv[10]
    
    data_name = ''.join(building_name, energy_type, 'Demand_kBtu', sep='_')
    '''
    
    start_logger()
    
    # Do not truncate numpy arrays when printing
    np.set_printoptions(threshold=np.nan)
    
    data_name = 'Ghausi_Electricity_Demand_kBtu'
    energy_type = 'OAT'
    _start = '2014'
    _end = 't'
    base_start = '2014-01'
    base_end = '2014-12'
    eval_start = '2015-01'
    eval_end = '2015-02'
    predict_start = '2020-01'
    predict_end = '2020-04'
    model_type = 0
    
    downloader = pipy_datalink()
    raw_data = downloader.get_stream_by_point(
        [data_name, energy_type], _start, _end)

    data_preprocessor = DataPreprocessor(raw_data)
    
    # 1 filter data periods
    # 2 separate datasets
    # 3 separate output and input
    cleaned_data = data_preprocessor.cleaned_data
    
    base_slice = (slice(base_start, base_end))
    training_data = np.array([cleaned_data.loc[base_slice, data_name]])
    training_data = np.transpose(training_data)
    target_values = np.array([cleaned_data.loc[base_slice, energy_type]])
    target_values = np.transpose(target_values)
    
    print training_data
    print target_values
    
    # 4 train a model
    clf = linear_model.LinearRegression()
    clf.fit(training_data, target_values)
    base_prediction = clf.predict(training_data)
    r2 = r2_score(target_values, base_prediction)
    print base_prediction
    print r2

    # 5 get scores for the model = validation
    eval_slice = (slice(eval_start, eval_end))
    eval_training_data = np.array([cleaned_data.loc[eval_slice, data_name]])
    eval_training_data = np.transpose(eval_training_data)
    eval_target = np.array([cleaned_data.loc[eval_slice, energy_type]])
    eval_target = np.transpose(eval_target)
    eval_predict = clf.predict(eval_training_data)
    r2 = r2_score(eval_target, eval_predict)
    print eval_predict
    print r2
    
    '''
    # 6 predict
    predict_slice = (slice(predict_start, predict_end))
    predict_training_data = np.array([cleaned_data.loc[predict_slice, data_name]])
    predict_training_data = np.transpose(predict_training_data)
    predict_target = np.array([cleaned_data.loc[predict_slice, energy_type]])
    predict_target = np.transpose(predict_target)
    extrapolated_data = clf.predict(predict_training_data)
    print extrapolated_data
    '''
    # 7 compare    
    #data = data_preprocessor.feature_extraction(cleaned_data)
    
    #TODO: Use command line arguments and talk with Raymund about this (sys.argv[...])
    #TODO: Refactor code
    #TODO: use DataFrame.to_json() at http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_json.html
    
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


def to_json(array):
    return json.dumps(array.tolist())



if __name__ == '__main__':
    try:
        main()
    except:
        # Logs and prints traceback
        logging.error(traceback.format_exc())
        sys.exit(1)