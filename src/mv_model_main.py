# Standard library imports
import json
import logging.config
import os
import sys
import time
import traceback

# Start logging temporarily with file object
sys.stderr = open("../logs/error.log", "w")
info_log = open("../logs/info.log", "w")
info_log.close()
date_format = time.strftime("%m/%d/%Y %H:%M:%S %p ")
sys.stderr.write(date_format + " - root - [WARNING] - ")

# Third-party library imports
import numpy as np
#import pandas as pd
import yaml

from sklearn import svm, cross_validation, linear_model, preprocessing, ensemble
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error

# Local imports
# New modules - marco.pritoni@gmail.com
from data_preprocessor import DataPreprocessor
from PIPy_Datalink import pipy_datalink


def main():
    # TODO: Documentation
    # TODO: Caching to speed up

    start_logger()

    # Do not truncate numpy arrays when printing
    np.set_printoptions(threshold=np.nan)

    # Test example
    building_name = "Ghausi"
    energy_type = "ChilledWater"
    model_type = "LinearRegression"
    base_start = "2014-01"
    base_end = "2014-12"
    base_start2 = "2016-01"
    base_end2 = "2016-12"
    eval_start = "2015-01"
    eval_end = "2015-12"
    predict_start = "2016-01"
    predict_end = "2016-12"

    # Check if number of command-line arguments is correctly set
    if len(sys.argv) == 12:
        building_name = sys.argv[1]
        energy_type = sys.argv[2]
        model_type = sys.argv[4]
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
    start = "2014"
    end = "t"

    data_name = "_".join([building_name, energy_type, "Demand_kBtu"])
    base_slice = (slice(base_start, base_end))
    base_slice2 = (slice(base_start2, base_end2))
    eval_slice = (slice(eval_start, eval_end))
    predict_slice = (slice(predict_start, predict_end))

    downloader = pipy_datalink()
    data_raw = downloader.get_stream_by_point([data_name, "OAT"], start, end)

    preprocessor = DataPreprocessor(data_raw)
    preprocessor.clean_data()
    preprocessor.add_degree_days(preprocessor.data_cleaned)
    preprocessor.add_time_features(preprocessor.data_preprocessed)
    preprocessor.create_dummies(preprocessor.data_preprocessed,
                                var_to_expand=["TOD", "DOW", "MONTH"])
    data = preprocessor.data_preprocessed

    output_vars = [data_name]
    input_vars = ["hdh", "cdh", u"TOD_0", u"TOD_1", u"TOD_2",
                  u"TOD_3", u"TOD_4", u"TOD_5", u"TOD_6", u"TOD_7", u"TOD_8", u"TOD_9",
                  u"TOD_10", u"TOD_11", u"TOD_12", u"TOD_13", u"TOD_14", u"TOD_15",
                  u"TOD_16", u"TOD_17", u"TOD_18", u"TOD_19", u"TOD_20", u"TOD_21",
                  u"TOD_22", u"TOD_23", u"DOW_0", u"DOW_1", u"DOW_2", u"DOW_3", u"DOW_4",
                  u"DOW_5", u"DOW_6", u"MONTH_1", u"MONTH_2", u"MONTH_3", u"MONTH_4",
                  u"MONTH_5", u"MONTH_6", u"MONTH_7", u"MONTH_8", u"MONTH_9", u"MONTH_10",
                  u"MONTH_11", u"MONTH_12"]
    
    # Idea: Create two different models 
    data_set = DataSet(data, base_slice, base_slice2, eval_slice, output_vars, input_vars)
    
    model_1 = Model(model_type)
    model_1.train(data_set.baseline1)
    model_1.project(data_set.eval)
    model_1.output()
    
    model_2 = Model(model_type)
    model_2.train(data_set.baseline2)
    model_2.project(data_set.eval)
    model_2.output()
    # model.predict(data_set.eval_in.values)

    # model.output()


"""Logging code"""
class StreamWriter():
    """Custom logger to wrap around file streams"""

    def __init__(self, name=__name__):
        self.logger = logging.getLogger(name)

    def write(self, message):
        self.logger.warn(message)


class InfoFilter(logging.Filter):
    """Filter to allow only INFO level messages to appear in info.log"""

    def __init__(self):
        super(InfoFilter, self).__init__("allow_info")

    def filter(self, record):
        if record.levelname == "INFO":
            return 1
        return 0


def start_logger():
    # Source: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
    default_path = "logging.yaml"
    default_level = logging.INFO
    env_key = "LOG_CFG"
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    sys.stderr.close()
    sys.stderr = StreamWriter()

"""Data"""


class DataSet(object):
    """
    Inspired by Paul Raftery Class:
    fist prototype

    the dataset_type field is to help standardize notation of different datasets:
           "A":"measured pre-retrofit data",
           "B":"pre-retrofit prediction with pre-retrofit model",
           "C":"pre-retrofit prediction with post-retrofit model",
           "D":"measured post-retrofit data",
           "E":"post-retrofit prediction with pre-retrofit model",
           "F":"post-retrofit prediction with pos-tretrofit model",
           "G":"TMY prediction with pre-retrofit model",
           "H":"TMY prediction with post-retrofit model"
    typical comparisons used by mave:
        Pre-retrofit model performance = A vs B
        Single model M&V = D vs E
        Post retrofit model performance  = D vs F
        Dual model M&V, normalized to tmy data = G vs H
    """

    def __init__(self, data,
                 tPeriod1=(slice(None)),
                 tPeriod2=(slice(None)),
                 tPeriod3=(slice(None)),
                 out=[""],
                 inp=[""]
                 ):

        # the attributes dynamically calculated using indices and column names
        # first draft duplicates datasets
        #self.baseline1_par={"inpt":{"slicer":(slice(None)), "col":[""]},"outpt":{"slicer":(slice(None)), "col":[""]}}
        #self.baseline1_par={"inpt": {"col": ["OAT"], "slicer":(slice(None))}, "outpt": {"col": ["Ghausi_Electricity_Demand_kBtu"], "slicer":(slice(None))}}

        self.fulldata = data
        self.baseline1 = {}
        self.baseline2 = {}
        self.eval = {}
        try:
            self.baseline1["in"] = data.loc[tPeriod1, inp]
        except:
            pass

        try:
            self.baseline1["out"] = data.loc[tPeriod1, out]
        except:
            pass

        try:
            self.baseline2["in"] = data.loc[tPeriod2, inp]
        except:
            pass

        try:
            self.baseline2["out"] = data.loc[tPeriod2, out]
        except:
            pass

        try:
            self.eval["in"] = data.loc[tPeriod3, inp]
        except:
            pass

        try:
            self.eval["out"] = data.loc[tPeriod3, out]
        except:
            pass

    def set_dataset(self, baseline_type, date_slicer, inpt, outpt):
        # need to develop a method to update stuff
        return

    def get_dataset(self, baseline_type, date_slicer, inpt_outpt):
        # ret=self.self.fulldata.loc[]

        return


class Model(object):
    """
    Measurement Verification Model.
    
    Parameters:
    model_type: String that describes the model type
    data_set: DataSet used to fit model and create projection
    
    Attributes:
    
    """
    
    def __init__(self, model_type, data_set=None):
        if model_type == "LinearRegression":
            self.clf = linear_model.LinearRegression()
        elif model_type == "RandomForest":
            self.clf = ensemble.RandomForestRegressor()
        else:
            self.clf = linear_model.LinearRegression()
            
        self.data_set = data_set
        self.baseline = {}
        self.eval = {}
        self.savings = {}
        self.scores = {}
        
        if data_set != None:
            self.baseline = data_set.baseline1
            self.eval = data_set.eval
            self.train(self.baseline)
            self.project(self.eval)
            
            
    def train(self, baseline):
        """Trains the model using baseline period data
        
        Parameters: 
        baseline: A dictionary with keys "in" and "out" that map to a pandas DataFrame
        """
        
        # Fit the data
        self.baseline = baseline
        self.clf.fit(baseline["in"], baseline["out"])
        baseline["out"]["Model"] = self.predict(baseline["in"].values)
        
        # Calculate scores 
        num_inputs = len(baseline["out"].columns)
        out_var = baseline["out"].columns[0]
        self.scores = self.calc_scores(baseline["out"], num_inputs, out_var)
            
        # separate train and evaluation functions
        """
        self.clf.fit(baseline.bs1_in, baseline.bs1_out)
        baseline.bs1_out["Model"] = self.clf.predict(baseline.bs1_in.values)
        baseline.eval_out["Model"] = self.clf.predict(baseline.eval_in.values)
        out_var = self.baseline.eval_out.columns[0]
        self.savings = baseline.eval_out["Model"] - baseline.eval_out[out_var]
        """
    def project(self, eval_data):
        self.eval = eval_data
        eval_data["out"]["Model"] = self.clf.predict(eval_data["in"].values)
        out_var = eval_data["out"].columns[0]
        self.savings = eval_data["out"]["Model"] - eval_data["out"][out_var]
        eval_data["savings"] = self.savings
        return self.savings
        
    def predict(self, data):
        return self.clf.predict(data)

    # compare is a two column dataframe with one column with output variable and one with the model prediction
    # p is the number of variables in the model (eg. count the columns in the
    # dataframe with input variables)
    @staticmethod
    def calc_scores(compare, p, out_var):
        scores = {}

        n = compare.count()[1]
        R2 = r2_score(compare[out_var], compare[["Model"]])  # this can be negative
        RMSE = ((mean_squared_error(compare[out_var], compare[["Model"]])) * n / (n - p))**(0.5)
        CV_RMSE = RMSE * 100 / compare[out_var].mean()
        NMBE = (compare.diff(axis=1)[["Model"]]).sum() / (compare[["Model"]].mean()) / (n - p) * 100
        scores["Adj_R2"] = 1 - (1 - R2) * (n - 1) / (n - p - 1)
        scores["RMSE"] = RMSE
        scores["CV_RMSE"] = CV_RMSE
        scores["NMBE"] = np.asscalar(NMBE)
        return scores

    # prints model outputs and relevant statistics
    def output(self):
        print(self.baseline["out"].to_json())
        print(self.eval["out"].to_json())
        print(self.savings.to_json())
        print(json.dumps(self.scores))

        # print()
if __name__ == "__main__":
    try:
        main()
    except:
        # Logs and prints traceback
        logging.error(traceback.format_exc())
        sys.exit(1)
