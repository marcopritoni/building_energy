# marco.pritoni@gmail.com



# Standard library imports
import json
import logging.config
import os
import sys
import traceback
import argparse

if __name__ == "__main__":
    # Start logging temporarily with file object
    sys.stderr = open("../logs/error.log", "w")
    info_log = open("../logs/info.log", "w")
    info_log.close()
    
    # date_format = time.strftime("%m/%d/%Y %H:%M:%S %p ")
    # sys.stderr.write(date_format + " - root - [WARNING] - ")

# Third-party library imports
import numpy as np
import yaml

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error

# Local imports
from preprocessor import DataPreprocessor
from get_data import get_point

tmy_name = "NSRDB.136708.OAT.TMY"

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
            self.clf = LinearRegression()
        elif model_type == "RandomForest":
            self.clf = RandomForestRegressor()
        else:
            self.clf = LinearRegression()
            
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
            
            
    def train(self, baseline, out_var):
        """Trains the model using baseline period data
        
        Parameters: 
        baseline: A dictionary with keys "in" and "out" that map to a pandas DataFrame
        """
        
        # Fit the data
        self.baseline = baseline
        self.clf.fit(baseline["in"], baseline["out"][out_var])
        baseline["out"]["Model"] = self.predict(baseline["in"].values)
        
        # Calculate scores 
        num_inputs = len(baseline["out"].columns)
        self.scores = self.calc_scores(baseline["out"], num_inputs, out_var)
        return self.scores 

    def project(self, eval_data, out_var):
        # Predicts in the period specified by eval_data
        self.eval = eval_data
        eval_data["out"]["Model"] = self.clf.predict(eval_data["in"].values)

        # Computes difference between model and actual
        self.savings = eval_data["out"]["Model"].copy()
        self.savings.sub(eval_data["out"][out_var], fill_value=0)
        eval_data["out"]["Savings"] = self.savings
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
        
        if len(self.eval) > 0:
            print(self.eval["out"].to_json())

        print(json.dumps(self.scores))


"""Logging code"""
class _StreamWriter():
    """Custom logger to wrap around file streams"""

    def __init__(self, name=__name__):
        self.logger = logging.getLogger(name)

    def write(self, message):
        self.logger.warn(message)


class _InfoFilter(logging.Filter):
    """Filter to allow only INFO level messages to appear in info.log"""

    def __init__(self):
        super(_InfoFilter, self).__init__("allow_info")

    def filter(self, record):
        if record.levelname == "INFO" or record.levelname == "DEBUG":
            return 1
        return 0
    
    
def main():
    # TODO: Documentation
    # TODO: Merging
    _start_logger()

    # Do not truncate numpy arrays when printing
    np.set_printoptions(threshold=np.nan)
    create_models()   
       
       
def create_models(args=None):
    """Create Measurement Verification models and prints data. Default args uses sys.argv"""
    args = _parse_args(args)
    data_name = "_".join([args.building_name, args.energy_type, "Demand_kBtu"])

    # Time period to request data from PI system
    # TODO: Change to actual dates
    start = "2014"
    end = "t"

    # Get data from PI system or local storage
    data_raw = get_point([data_name, "OAT"], start, end)
    data = preprocess(data_raw)

    # Create time slice objects for data_set
    base_slice = (slice(args.base_start, args.base_end))
    base_slice2 = base_slice
    eval_slice = base_slice
    
    if args.subparser_name == "simple":
        eval_slice = (slice(args.eval_start, args.eval_end))   
    elif args.subparser_name == "tmy":
        base_slice2 = (slice(args.base_start2, args.base_end2))

    output_vars = [data_name]
    input_vars = ["hdh", "cdh", u"TOD_0", u"TOD_1", u"TOD_2",
                  u"TOD_3", u"TOD_4", u"TOD_5", u"TOD_6", u"TOD_7", u"TOD_8", u"TOD_9",
                  u"TOD_10", u"TOD_11", u"TOD_12", u"TOD_13", u"TOD_14", u"TOD_15",
                  u"TOD_16", u"TOD_17", u"TOD_18", u"TOD_19", u"TOD_20", u"TOD_21",
                  u"TOD_22", u"TOD_23", u"DOW_0", u"DOW_1", u"DOW_2", u"DOW_3", u"DOW_4",
                  u"DOW_5", u"DOW_6"]
    
    # Create a DataSet with OAT values in output as column
    data_set = DataSet(data, base_slice, base_slice2, eval_slice, output_vars, input_vars)   
    data_set.baseline1["out"]["OAT"] = data.loc[base_slice, "OAT"]
    data_set.baseline2["out"]["OAT"] = data.loc[base_slice2, "OAT"]
    data_set.eval["out"]["OAT"] = data.loc[eval_slice, "OAT"]
    
    # Create first model for baseline period 1 
    model_1 = Model(args.model_type)
    model_1.train(data_set.baseline1, data_name)
    
    if args.subparser_name == "simple":
        model_1.project(data_set.eval, data_name)
        model_1.output()
        return model_1
    
    elif args.subparser_name == "tmy":
        tmy_slice = (slice(args.tmy_start, args.tmy_end))
        tmy_raw = get_point(tmy_name, args.tmy_start, args.tmy_end)
        
        # Renamed to OAT to be compatible with preprocessor
        tmy_raw.rename(columns={tmy_raw.columns[0]: "OAT"}, inplace=True)
        
        tmy_data = preprocess(tmy_raw)  
        eval_data = format_eval(data, tmy_data, tmy_slice, input_vars, output_vars)
        
         # Create second model for baseline period 2 
        model_2 = Model(args.model_type)
        model_2.train(data_set.baseline2, data_name)
        
         # Projects data_name into TMY period
        model_1.project(eval_data, data_name)
        eval_data["out"]["Baseline 1"] = eval_data["out"]["Model"].copy()
        model_2.project(eval_data, data_name)
        eval_data["out"]["Baseline 2"] = eval_data["out"]["Model"].copy()
        eval_data["out"].drop(["Model"], inplace=True, axis=1)
        
        # Get savings over typical TMY period by subtracting from two baseline model results
        savings = eval_data["out"]["Baseline 2"].copy()
        savings = savings.sub(eval_data["out"]["Baseline 1"], fill_value=0)
        eval_data["out"]["Savings"] = savings

        print(eval_data["out"].to_json())
        return {1: model_1, 2: model_2, 3: eval_data}

def preprocess(data):
    preprocessor = DataPreprocessor(data)
    preprocessor.clean_data()
    preprocessor.add_degree_days(preprocessor.data_cleaned)
    preprocessor.add_time_features(preprocessor.data_preprocessed)
    preprocessor.create_dummies(preprocessor.data_preprocessed,
                                var_to_expand=["TOD", "DOW", "MONTH"])
    return preprocessor.data_preprocessed

def format_eval(data, tmy_data, tmy_slice, input_vars, output_vars):
    eval_data = {}
    eval_data["in"] = tmy_data.loc[tmy_slice, input_vars]
    eval_data["out"] = tmy_data.loc[tmy_slice, ["OAT"]]
    
    for var in output_vars:
        eval_data["out"][var] = data.loc[tmy_slice, var]
        
    return eval_data

def _start_logger():
    # Source: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
    logger = logging.getLogger(__name__)
    logger.addFilter(_InfoFilter())
    
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
    sys.stderr = _StreamWriter()

def _parse_args(args):
    """Parses command line arguments using argparse"""
    
    parser = argparse.ArgumentParser(description="A tool for mechanical engineers at the UC Davis Energy Conservation Office to analyze the energy performance of UC Davis buildings.", 
        fromfile_prefix_chars="@")
    
    subparsers = parser.add_subparsers(dest="subparser_name")
    tmy_parser = subparsers.add_parser("tmy")
    tmy_parser.add_argument("building_name", help="building to perform analysis on")
    tmy_parser.add_argument("energy_type", help="data for selected fuel type")
    tmy_parser.add_argument("model_type", choices=["LinearRegression", "RandomForest"])
    tmy_parser.add_argument("base_start", help="starting period of baseline 1. YEAR-MONTH (ex. 2016-01)")
    tmy_parser.add_argument("base_end", help="end period of baseline 2. YEAR-MONTH (ex. 2016-01)")
    tmy_parser.add_argument("base_start2", help="starting period of baseline 2")
    tmy_parser.add_argument("base_end2", help="end period of baseline 2")
    tmy_parser.add_argument("tmy_start", help="tmy start period")
    tmy_parser.add_argument("tmy_end", help="tmy end period")

    simple_parser = subparsers.add_parser("simple")
    simple_parser.add_argument("building_name", help="building to perform analysis on")
    simple_parser.add_argument("energy_type", help="data for selected fuel type")
    simple_parser.add_argument("model_type", choices=["LinearRegression", "RandomForest"])
    simple_parser.add_argument("base_start", help="starting period of baseline 1. YEAR-MONTH (ex. 2016-01)")
    simple_parser.add_argument("base_end", help="end period of baseline 2. YEAR-MONTH (ex. 2016-01)")
    simple_parser.add_argument("eval_start", help="evaluation start period")
    simple_parser.add_argument("eval_end", help="evaluation end period")
    
    # See https://stackoverflow.com/a/29293080
    # Prints help message on invalid input
    try:
        return parser.parse_args(args)
    
    except SystemExit as err: 
        # If error is unhandled 
        if err.code == 2: 
            parser.print_help() 
            if sys.argv[1] == "simple": 
                simple_parser.print_help() 
            elif sys.argv[1] == "tmy": 
                tmy_parser.print_help() 
            else: 
                parser.print_help() 
 
        # Exit if parsing error regardless
        sys.exit()
        
if __name__ == "__main__":
    try:
        main()
        
    # Graceful exit due to parse error or intentional sys.exit() call
    except SystemExit:
        sys.exit()      
          
    except:
        # Logs and prints traceback
        logging.error(traceback.format_exc())
        sys.exit(1)
