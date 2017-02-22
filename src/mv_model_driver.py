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
    downloader = pipy_datalink()
    raw_data = downloader.get_stream_by_point(
        ['Ghausi_Electricity_Demand_kBtu', 'OAT'], _start="2014", _end="t")

    data_processor = Data_Preprocessor(raw_data)
    
    # 1-3
    timeSlicer = (slice("2014-01", "2014-12"))
    data_name = 'Ghausi_Electricity_Demand_kBtu'
    cleaned_data = data_processor.data_cleaned
    var = []
    train_data = cleaned_data.loc[timeSlicer, var]
    train_target = cleaned_data.loc[timeSlicer, data_name]

    print("Middle")
    print(train_target)
    # 4
    clf = linear_model.LinearRegression()
    model = clf.fit(train_data[:-1], train_target[:-1])
    """
    # 5
    #model.score(data_train,target_train)
    
    # 6
    predictions = model.predict(cleaned_data)
    
    # 7
    compare = pd.DataFrame(predictions)
    #compare.columns = ["target_actual"]
    #compare["target_predicted"] = predictions   

    score = model.score(cleaned_data, predictions)
    print(score)"""


if __name__ == "__main__":
    main()
