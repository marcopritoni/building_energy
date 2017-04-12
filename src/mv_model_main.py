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
    #TODO: Documentation of this function
    #TODO: Caching to speed up

    start_logger()
    
    # Do not truncate numpy arrays when printing
    np.set_printoptions(threshold=np.nan)
        
    # Test example
    building_name = 'Ghausi'
    energy_type = 'ChilledWater'
    base_start = '2014-01'
    base_end = '2014-12'
    eval_start = '2015-01'
    eval_end = '2015-12'
    predict_start = '2016-01'
    predict_end = '2016-12'
           
    # Check if command-line arguments are correctly set
    if(len(sys.argv) == 11):
        building_name = sys.argv[1]
        energy_type = sys.argv[2]
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

    data_name = '_'.join([building_name, energy_type, 'Demand_kBtu'])
    print data_name 
    
    # Time period to request data from PI system
    start = '2014'
    end = 't'
    model_type = 0
    
    model = Model(data_name, base_start, base_end, eval_start, eval_end, 
                  predict_start, predict_end, start, end)
    
    model.train_model()
    model.predict_model()
    model.output()
    
#     base_slice = (slice(base_start, base_end))
#     eval_slice = (slice(eval_start, eval_end))
#     predict_slice = (slice(predict_start, predict_end))
#     
#     downloader = pipy_datalink()
#     data_raw = downloader.get_stream_by_point([data_name, 'OAT'], start, end)
# 
#     preprocessor = DataPreprocessor(data_raw)
#     preprocessor.clean_data()
#     preprocessor.add_degree_days(preprocessor.data_cleaned)
#     preprocessor.add_time_features(preprocessor.data_preprocessed)
#     preprocessor.create_dummies(preprocessor.data_preprocessed, var_to_expand=['TOD','DOW','MONTH'])
#     data = preprocessor.data_preprocessed
    '''
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
#     out = [data_name]
#     inp = ['hdh', 'cdh', u'TOD_0', u'TOD_1', u'TOD_2',
#            u'TOD_3', u'TOD_4', u'TOD_5', u'TOD_6', u'TOD_7', u'TOD_8', u'TOD_9',
#            u'TOD_10', u'TOD_11', u'TOD_12', u'TOD_13', u'TOD_14', u'TOD_15',
#            u'TOD_16', u'TOD_17', u'TOD_18', u'TOD_19', u'TOD_20', u'TOD_21',
#            u'TOD_22', u'TOD_23', u'DOW_0', u'DOW_1', u'DOW_2', u'DOW_3', u'DOW_4',
#            u'DOW_5', u'DOW_6', u'MONTH_1', u'MONTH_2', u'MONTH_3', u'MONTH_4',
#            u'MONTH_5', u'MONTH_6', u'MONTH_7', u'MONTH_8', u'MONTH_9', u'MONTH_10',
#            u'MONTH_11', u'MONTH_12']
#     
#     clf = linear_model.LinearRegression()
#     data_set = DataSet(data, base_slice, eval_slice, predict_slice, out, inp)
#     model = clf.fit(data_set.bs2_in, data_set.bs2_out)
#     score = model.score(data_set.bs2_in.values, data_set.bs2_out.values)
#     model.predict(data_set.bs2_in.values)
#     
#     output = data_set.bs2_out
#     output["prediction"] = model.predict(data_set.bs2_in.values)
#     
#     print output.to_json()
#     print(score)
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
    
    #TODO: Use command line arguments and talk with Raymund about this (sys.argv[...])
    #TODO: Refactor code
    #TODO: use DataFrame.to_json() at http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_json.html
    
    #Savings
    P1 = Plotter()
    #PrePostSav
    #pps = P1.plot_PrePostSav_byMo(data_set.fulldata, data_name)
    #print pps.to_json()
    
    #ModPostSav
    #mps = P1.plot_ModPostSav_byMo(data_set.fulldata, data_name)
    #print mps.to_json()
    
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
        
        # the attributes dynamically calcylated using indices and column names
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

class Plotter(object):


    # data manipulation methods
    
    def unstack_(self):
        return
    
    def add_timeColumn(self,data, timecol):
        
        # need to be more flexible, this is a placeholder
        if isinstance(timecol, list):
            for elem in timecol:
                
                if elem=="TOD":
                    
                
                    data[elem]=data.index.hour
                
                elif elem=="YR-MO":
                    
                    year=pd.Series(data.index.year, index=data.index)
                    month=pd.Series(data.index.month,index=data.index).map("{:02}".format)
                    data.loc[:,elem]=(year.astype(str) +"-" + (month.astype(str)))
        
        return data

    def filterWeekDay(self,data):
        return data[(data.index.weekday <5)]
        # data.index.weekday == 0 is Monday 
        # data.index.weekday == 6 is Sunday 
    
    def filterWeekEnd(self,data):
        return data[((data.index.weekday > 4)&(data.index.weekday <=6))]
        # data.index.weekday == 0 is Monday 
        # data.index.weekday == 6 is Sunday 
    
    # plotting methods: 1- LineCharts
    
    def plot_energy_profile_byMo (self,
                                  data,
                                  start_, 
                                  end_, 
                                  var):
        # daily energy profile by Month (each line is an avergage month)
        # 1. select rows (time interval) and columns (variable)
        tSlicer=(slice(start_,end_))
        data=pd.DataFrame(data.loc[tSlicer,var])
        
        # 2. add time columns
        data=self.add_timeColumn(data, ["TOD","YR-MO"])
        
        # 3. reshape unstacking
        data_unstacked=data.groupby(["TOD","YR-MO"]).mean().unstack()
        
        # 4. format plot
        n=len(data_unstacked.columns)
        #color=cm.rainbow(np.linspace(0,1,n))
        
        # 5. plot
        data_unstacked.plot(figsize=(15,5),label=var, title=var,ylim=[0,data_unstacked.max().max()*1.1])
        
        return
        
        
    # plotting methods: 2- ScatterPlots
              
    def plot_scatter_WD_WE (self,
                    data, 
                    start_, 
                    end_, 
                    var_out,
                    var_in):
        
        # 1. select rows (time interval) and columns (variable)
        tSlicer=(slice(start_,end_))
        data=pd.DataFrame(data.loc[tSlicer,[var_in,var_out]])

        # 2. setup plots
        fig, ax = plt.subplots()

        # 3. select/plot WD

        WD_data=self.filterWeekDay(data)
        WD_data.loc[tSlicer, :].plot(figsize=(18,5), kind="scatter", x=var_in,y=var_out,
                                     label='WeekDay', color='r', ax=ax).set_title(var_out+" Week Days");

        # 4. select/plot WE

        WE_data=self.filterWeekEnd(data)
        WE_data.loc[tSlicer, :].plot(figsize=(18,5), kind="scatter", x=var_in,y=var_out,
                                     label='WeekEnd', color='g', ax=ax).set_title(var_out+" Week Days");
            
        return


    
### need to rewrite after this

    def plot_scatter_Per1vsPer2 (self,
                      data_per1,
                      data_per2,
                      var_out,
                      var_in,
                      var_out2=None,
                      var_in2=None      
                                ):
        
#        if var_in2:
        var_in2=var_in

#        if var_out2:
        var_out2=var_out
        
        # this method assumes the datasets are already separated and sliced in time
        # it also assumes the two in/out variables have the same name

        # 2. setup plots
        fig, ax = plt.subplots()

        # 3. plot per1

        data_per1.plot(figsize=(18,5), kind="scatter", x=var_in,y=var_out,
                                     label='Period 1', color='r', ax=ax).set_title(var_out+" Period 1");

        # 4. plot per2

        #WE_data.plot(figsize=(18,5), kind="scatter", x=var_in2,y=var_out2,
        #                             label='WeekEnd', color='g', ax=ax).set_title(var_out+" Week Days");
            
 
        return

    def plot_compare (self,
                      compare_data,
                      plot_start,
                      plot_end,
                      tar):
        compare = compare_data.loc[plot_start:plot_end,:]#.plot(figsize=(15,5),title=tar)#.set_title("month = %d" %month)
        
        return compare 
        #plt.show() 

    def plot_PrePost_byMo (self,
                           data, 
                           tar):
        last_mo=data[data["PrePost"]==1].index.max().month
        temp=data.groupby(["MONTH","YEAR"])[tar].mean().unstack()
        temp[(temp.index<=last_mo)].plot(figsize=(15,5), kind="bar",title=tar)
        plt.show()

    def plot_ModPost_byMo (self,
                           compare_sav, 
                           tar):
        cols=["target_predicted", "target_actual"]
        compare_sav = compare_sav.ix[:, cols]
        compare_sav.groupby(compare_sav.index.month).mean().plot(figsize=(15,5), kind="bar",title=tar)
        plt.show()

    def plot_PrePostSav_byMo(self,
                             data, 
                             tar):
        '''
            No PrePost field retrieved from data; gives an error
            hardcoding to 1 for now
        '''
        last_mo=1#data[data["PrePost"]==1].index.max().month
        temp=data.groupby(["MONTH","YEAR"])[tar].mean().unstack()
        prepostsav = (temp[(temp.index<=last_mo)].diff(axis=1)*(-1))#.plot(figsize=(15,5), kind="bar",title=tar)
        
        return prepostsav
        #plt.show()

    def plot_ModPostSav_byMo(self,
                             compare_sav, 
                             tar):
        cols=["target_predicted", "target_actual"]
        compare_sav = compare_sav.ix[:, cols]
        modpostsav = (compare_sav.groupby(compare_sav.index.month).mean().diff(axis=1)*(-1))#.plot(figsize=(15,5), kind="bar",title=tar)
        
        return modpostsav
        #plt.show() 
        
        
    # plotting methods: 3- BarCharts
    
    
    
    # plotting methods: 4- BoxPlot

    
    
    # plotting methods: 5- Heat Mapsd
    
class Model(object):
    self.data
    self.data_set 
    self.output
    self.score
    
    def __init__(self, data_name, base_s, base_e, eval_s, eval_e, predict_s, predict_e, s, e):
        out = [data_name]
        inp = ['hdh', 'cdh', u'TOD_0', u'TOD_1', u'TOD_2',
           u'TOD_3', u'TOD_4', u'TOD_5', u'TOD_6', u'TOD_7', u'TOD_8', u'TOD_9',
           u'TOD_10', u'TOD_11', u'TOD_12', u'TOD_13', u'TOD_14', u'TOD_15',
           u'TOD_16', u'TOD_17', u'TOD_18', u'TOD_19', u'TOD_20', u'TOD_21',
           u'TOD_22', u'TOD_23', u'DOW_0', u'DOW_1', u'DOW_2', u'DOW_3', u'DOW_4',
           u'DOW_5', u'DOW_6', u'MONTH_1', u'MONTH_2', u'MONTH_3', u'MONTH_4',
           u'MONTH_5', u'MONTH_6', u'MONTH_7', u'MONTH_8', u'MONTH_9', u'MONTH_10',
           u'MONTH_11', u'MONTH_12']
        base_start = base_s
        base_end = base_e
        eval_start = eval_s
        eval_end = eval_s
        predict_start = predict_s
        predict_end = predict_e
        start = s
        end = e
        
    def process_data(self):
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
    
    def train_model(self):
        process_data()
        
        clf = linear_model.LinearRegression()
        data_set = DataSet(data, base_slice, eval_slice, predict_slice, out, inp)
        model = clf.fit(data_set.bs2_in, data_set.bs2_out)
        score = model.score(data_set.bs2_in.values, data_set.bs2_out.values)
        model.predict(data_set.bs2_in.values)

    def predict_model(self):
        output = data_set.bs2_out
        output["prediction"] = model.predict(data_set.bs2_in.values)
    
    def output(self):
        print output.to_json()
        print(score)
    
if __name__ == '__main__':
    try:
        main()
    except:
        # Logs and prints traceback
        logging.error(traceback.format_exc())
        sys.exit(1)
