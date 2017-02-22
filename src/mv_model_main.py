import datetime
import json
import matplotlib
import mv_script_marco
import numpy as np
import os
import pandas as pd
import requests as req
import sys

from matplotlib import style
#%matplotlib inline
style.use('ggplot')


#  new modules - marco.pritoni@gmail.com
from PIPy_Datalink import *
from data_preprocessor import *

from sklearn import svm, cross_validation, linear_model, preprocessing, ensemble
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error

# Steps
# 1 filter data periods
# 2 separate datasets
# 3 separate output and input
# 4 train a model
# 5 get scores for the model = validation
# 6 predict
# 7 compare


def main():
    """
    TODO: Documentation of this function
    """
    
    downloader = pipy_datalink()
    raw_data = downloader.get_stream_by_point(
        ['Ghausi_Electricity_Demand_kBtu', 'OAT'], _start="2014", _end="t")

    data_preprocessor = DataPreprocessor(raw_data)
    
    # 1-3
    timeSlicer = (slice("2014-01", "2014-12"))
    data_name = 'Ghausi_Electricity_Demand_kBtu'
    cleaned_data = data_preprocessor.cleaned_data
    
    data = cleaned_data
    
    #TODO: Use command line arguments and talk with Raymund about this (sys.argv[...])
    #TODO: Refactor code
    #TODO: use DataFrame.to_json() at http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_json.html
    
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


if __name__ == "__main__":
    main()
