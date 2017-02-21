import pandas as pd
import os
import requests as req
import json
import numpy as np
import datetime

from matplotlib import style
import matplotlib
#%matplotlib inline
style.use('ggplot')


#  new modules - marco.pritoni@gmail.com
from PIPy_Datalink import *
from Data_Preprocessor import *

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
    downloader = pipy_datalink()
    data_processor =  data_preprocessor(
                        temp,
                        
                        runInterpolate=False,
                        
                        runRemoveNA=False,
                       
                        runRemoveOutliers=True,
                       
                        runRemoveOutOfBound=False,
                       
                        runResample=False,
                       
                        runExtendIndex=False,
                       
                        time_res="h",
                       
                        sd_val=3,
                       
                        low_bound=0,
                       
                        high_bound=9998,
                       
                        freq="h"                    
                        
                        )
    # 1-3
    timeSlicer = (slice("2014-01", "2014-12"))
    data_name = 'Ghausi_Electricity_Demand_kBtu'
    data_preprocessor.data_cleaned.loc[timeSlicer, data_name]
    
    # 4
    model = linear_model.LinearRegression()
    model_coeff.mod.fit()
    
    # 5
    
    # 6
    model_coeff.predict()
    
    # 7


if __name == "__main__":
    main()
