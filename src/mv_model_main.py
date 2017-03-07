# Standard library imports
import json
import logging.config
import os
import sys
import time

# Start logging temporarily with file object
sys.stderr = open('../logs/error.log', 'w')
info_log = open('../logs/info.log', 'w')
info_log.close()
date_format = time.strftime("%m/%d/%Y %H:%M:%S %p ")
sys.stderr.write(date_format + " - root - [ERROR] - " + os.linesep)

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

    """
    Gets user input from command line and sets to the variables that will be used to retrieve and process data
    data_name = raw_input("Enter building name: ")
    energy_type = raw_input("Enter energy type: ")
    start = raw_input("Enter start date: ")
    end = raw_input("Enter end date: ")
    base_start = raw_input("Enter baseline start date: ")
    base_end = raw_input("Enter baseline end date: ")
    eval_start = raw_input("Enter validation start date: ")
    eval_end = raw_input("Enter validation end date: ")
    predict_start = raw_input("Enter prediction start date: ")
    predict_end = raw_input("Enter prediction end date: ")
    """
    
    """
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
    
    data_name = ''.join(building_name, energy_type, "Demand_kBtu", sep='_')
    """
    
    start_logger()
    
    # Do not truncate numpy arrays when printing
    np.set_printoptions(threshold=np.nan)
    
    data_name = 'Ghausi_Electricity_Demand_kBtu'
    energy_type = "OAT"
    _start = "2014"
    _end = "t"
    base_start = '2014-01'
    base_end = '2014-12'
    eval_start = '2015-01'
    eval_end = '2015-02'
    predict_start = '2020-01'
    predict_end = '2020-04'
    model_type = 0;
    
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
    
    """
    # 6 predict
    predict_slice = (slice(predict_start, predict_end))
    predict_training_data = np.array([cleaned_data.loc[predict_slice, data_name]])
    predict_training_data = np.transpose(predict_training_data)
    predict_target = np.array([cleaned_data.loc[predict_slice, energy_type]])
    predict_target = np.transpose(predict_target)
    extrapolated_data = clf.predict(predict_training_data)
    print extrapolated_data
    """
    # 7 compare    
    #data = data_preprocessor.feature_extraction(cleaned_data)
    
    #TODO: Use command line arguments and talk with Raymund about this (sys.argv[...])
    #TODO: Refactor code
    #TODO: use DataFrame.to_json() at http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_json.html
    """   
    # TASKS
    explor = False  # plots exploratory graphs
    search = True  # iterates to get best model

    # define pre-post
    pre_start = pd.to_datetime(
        '4,1,2016',  format='%m,%d,%Y', errors='coerce', dayfirst=False)
    pre_end = pd.to_datetime(
        '11,1,2016', format='%m,%d,%Y', errors='coerce', dayfirst=False)
    post_start = pd.to_datetime(
        '11,1,2016', format='%m,%d,%Y', errors='coerce', dayfirst=False)
    post_end = pd.to_datetime(
        '11,1,2017', format='%m,%d,%Y', errors='coerce', dayfirst=False)
    data["PrePost"] = np.nan
    data.loc[pre_start:pre_end, "PrePost"] = 0
    data.loc[post_start:post_end, "PrePost"] = 1

    # select energy type variables
    energy_type = ["chw", "elec", "steam"]
    # energy_type=["chw"]
    # select other regressors
    var = ['hdh', 'cdh']
    # select regression algorithm
    algorithm = 2
    mod_type = 2

    # FOR LOOP 1: cycle through energy types
    score_tot = {}
    saving_cost = {}
    saving_perc = {}
    uncert_tot = {}

    # as an alternative to define it explicitely use k-fold cross validation
    # with sci-kit learn...
    for tar in energy_type:

        # Training Period - Use the full period, then the validation will be
        # dropped later
        train_start = pre_start
        train_end = pre_end
        # Validation Period; va
        val_start = pd.to_datetime(
            '4,1,2015',  format='%m,%d,%Y', errors='coerce', dayfirst=False)
        val_end = pd.to_datetime(
            '4,7,2015',  format='%m,%d,%Y', errors='coerce', dayfirst=False)

        # period to calculate savings over
        pred_start = post_start
        pred_end = post_end

        data.loc[train_start:train_end, "Period"] = 1
        data.loc[val_start:val_end, "Period"] = 2
        data.loc[pred_start:pred_end, "Period"] = 3

        print "Target Var is        %s" % (tar)
        print "Training time range:   %s - %s" % (train_start, train_end)
        print "Validation time range: %s - %s" % (val_start, val_end)
        print data

        # TRAIN MODEL
        ret_obj = train_model(data, tar, var, algorithm,
                              mod_type, train_start, train_end, val_start, val_end)

        # save results
        curr_model = ret_obj["model"]
        model_col = ret_obj["model_col"]
        model_data = ret_obj["model_data"]
        score_train = ret_obj["score"]
        target_modeled_train = ret_obj["target_modeled_train"]
        compare_train = ret_obj["compare"]
        # temp=ret_obj["data_train"]
        print compare_train

        # save scores
        score_tot[tar] = {}
        score_tot[tar]["score_train"] = calc_scores(
            compare_train, len(model_col))
        print "score train = "
        print score_tot[tar]["score_train"]

        # PREDICT AND COMPARE
        ret_obj2 = predict_model(
            model_data, tar, model_col, curr_model, val_start, val_end)

        # save results
        score_val = ret_obj2["score"]
        target_modeled_val = ret_obj2["target_modeled_val"]
        compare_val = ret_obj2["compare"]

        score_tot[tar]["score_val"] = calc_scores(compare_val, len(model_col))
        print "score val = "
        print score_tot[tar]["score_val"]
        print "\n"
        score_table = pd.Panel(score_tot).transpose(
            1, 0, 2).to_frame()  # build score table
        print score_table
        
        # CALCULATE SAVINGS
        ret_obj3 = calc_savings(
            model_data, tar, model_col, curr_model, pred_start, pred_end)
        compare_sav = ret_obj3["compare"]

        ret_obj4 = savings_table_byMo(compare_sav, tar, cost)
        saving_cost.update(ret_obj4["data_cost_sav"])
        saving_perc.update(ret_obj4["data_perc_sav"])
        print ret

        # UNCERTAINTY
        # uncert_tot.update(calc_uncert)
        print calc_uncert(compare_train, compare_sav, 95, score_tot, tar, absol=True)
"""    
class Logger(logging.Logger):
    """Custom logger to wrap around file streams"""
    
    def __init__(self, name = __name__):
        self.logger = logging.getLogger(name)
        
    def write(self, message):
        self.logger.error(message)
        
        
def start_logger():   
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
    
    sys.stderr = Logger()

def to_json(array):
    return json.dumps(array.tolist())

if __name__ == "__main__":
    main()