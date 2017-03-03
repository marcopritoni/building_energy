'''
Preprocesses and cleans data.

@author Marco Pritoni <marco.pritoni@gmail.com>
latest update: Feb 14 2017

TODO:

-think about best way of interpolating/resampling (1-groupby TimeGrouper, resample, interpolate)
-save the list of point removed
-add preprocessing as in mave (data normalization around 0)

version 0.1
'''

import logging

import numpy as np
import pandas as pd
from scipy import stats

class DataPreprocessor(object):
    """Preprocessor class for data cleaning and manipulation
    (standardization for machine learning)
    """

    def __init__(self, df):
        self.interpolating = True
        self.na_removed = True
        self.outliers_removed = True
        self.bounds_enforced = True
        self.resampling = True
        self.run_extend_index = False
        self.time_res = "h"
        self.sd_val = 3
        self.low_bound = 0
        self.high_bound = 9998
        self.freq = "h"
        self.raw_data = df
        self.cleaned_data = self.clean_data(df)
         
    def interpolate_data(self, data, time_res):
        data = data.groupby(pd.TimeGrouper(time_res)).mean()
        # may want to look into resample() or interpolate() method
        # alternatively
        return data

    #
    def remove_na(self, data):
        return data.dropna()

    def remove_outliers(self, data, sd_val):
        """Removes all data data above or below sd_val standard deviations
        from the mean and excludes all lines with NA in any column"""

        data = data.dropna()[
            (np.abs(stats.zscore(data.dropna())) < float(sd_val)).all(axis=1)]

        return data

    def remove_out_of_bound(self, data, low_bound,
                            high_bound):
        data = data.dropna()
        data = data[(data > low_bound).all(axis=1) &
                    (data < high_bound).all(axis=1)]

        return data

    def resample_data(self, data, freq):
        return data.resample(freq).mean()

    def extend_index(self):
        return

    def clean_data(self, data):
        # save the instance of the DataSet(DataFrame) in a local variable
        # this allows to use DataSet methods such as data.interpolate()

        # data=self
        logger = logging.getLogger(__name__)
        logger.info("Starting data cleaning")
        
        # apply these methods with this sequence
        if self.interpolating:
            # time_res="h"
            try:
                data = self.interpolate_data(data, self.time_res)
                logger.info("Interpolated data")

            except:
                logger.error("Failed to interpolate data")

        if self.na_removed:
            try:
                data = self.remove_na(data)
                logger.info("Removed NA data")

            except:
                logger.error("Failed to remove NA data")
                
        
        if self.outliers_removed:
            # sd_val=3
            try:
                data = self.remove_outliers(data, self.sd_val)
                logger.info("Removed outlier from data")

            except:
                logger.error("Failed to remove outlier from data")
        
        if self.bounds_enforced:
            # low_bound=0
            # high_bound=9998
            try:
                data = self.remove_out_of_bound(data, self.low_bound, self.high_bound)
                logger.info("Removed out of bounds data")

            except:
                logger.error("Failed to remove out of bounds data")
        
        if self.resampling:
            # freq="d"
            try:
                data = self.resample_data(data, self.freq)
                data = self.remove_na(data)
                logger.info("Re-sampled data")

            except:
                logger.error("Failed to re-sample data")
        
        if self.run_extend_index:
            try:
                print "testing"

            except:
                pass

        return data

    def feature_extraction(self, data):
        data["YEAR"] = data.index.year
        data["MONTH"] = data.index.month
        data["TOD"] = data.index.hour
        data["DOW"] = data.index.weekday
        data["WEEK"] = data.index.week
        data["DOY"] = data.index.dayofyear
        return
