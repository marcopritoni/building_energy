"""
Preprocesses and cleans data.

@author Marco Pritoni <marco.pritoni@gmail.com>
latest update: Feb 14 2017

TODO:

-think about best way of interpolating/resampling (1-groupby TimeGrouper, resample, interpolate)
-save the list of point removed
-add preprocessing as in mave (data normalization around 0)

version 0.1
"""

# Standard library imports
import logging

# Third-party library imports
import numpy as np
import pandas as pd
from scipy import stats


class DataPreprocessor(object):
    """Preprocessor class for data cleaning and manipulation
    (standardization for machine learning)
    """

    def __init__(self, df, *args, **kwargs):
        self.data_raw = df
        self.data_cleaned = df
        self.data_removed = pd.DataFrame()
        self.data_preprocessed = pd.DataFrame()
        self.droppedNA = pd.Series()
        self.droppedOutliers = pd.Series()
        self.droppedOutOfBound = pd.Series()

    def resample_data(self, data, freq):
        return data.resample(freq).mean()
    
    def interpolate_data(self, data, interpolate_limit):
        return data.interpolate(how="index", limit=interpolate_limit)

    def remove_na(self, data, na_how):
        return data.dropna(how=na_how)

    def remove_outliers(self, data, sd_val):
        """Removes all data data above or below sd_val standard deviations
        from the mean and excludes all lines with NA in any column"""

        data = data.dropna()[
            (np.abs(stats.zscore(data.dropna())) < float(sd_val)).all(axis=1)]

        return data

    def remove_out_of_bound(self, data, low_bound, high_bound):
        data = data.dropna()
        data = data[(data > low_bound).all(axis=1) & 
                    (data < high_bound).all(axis=1)]

        return data


    def clean_data(self,
                   resampling=True,
                   freq="h",
                   interpolating=True,
                   interpolate_limit=1,
                   removing_na=True,
                   na_how="any",
                   removing_outliers=True,
                   sd_val=3,
                   enforcing_bounds=True,
                   low_bound=0,
                   high_bound=9998,
                   *args,
                   **kwargs):
        # save the instance of the DataSet(DataFrame) in a local variable
        # this allows to use DataSet methods such as data.interpolate()

        # data=self
        logging.info("Starting data cleaning")
        data = self.data_raw
        
        if resampling:
            # freq="d"
            try:
                data = self.resample_data(data, freq)
                data = self.remove_na(data, na_how)
                logging.info("Re-sampled data at {0}".format(freq))

            except:
                logging.warning("Failed to re-sample data at {0}".format(freq))
                        
        if interpolating:
            # time_res="h"
            try:
                data = self.interpolate_data(data, interpolate_limit)
                logging.info("Interpolated data with limit {0}".format(interpolate_limit))

            except:
                logging.warning("Failed to interpolate data with limit {0}".format(interpolate_limit))

        if removing_na:
            try:
                data = self.remove_na(data, na_how)
                logging.info("Removed NA data")

            except:
                logging.warning("Failed to remove NA data")

        if removing_outliers:
            # sd_val=3
            try:
                data = self.remove_outliers(data, sd_val)
                logging.info("Removed outlier from data")

            except:
                logging.warning("Failed to remove outlier from data")

        if enforcing_bounds:
            # low_bound=0
            # high_bound=9998
            try:
                data = self.remove_out_of_bound(data, low_bound, high_bound)
                logging.info("Removed out of bounds data")

            except:
                logging.warning("Failed to remove out of bounds data")
        
        self.data_cleaned = data
        return data


    def flag_data(self,
                    runRemoveNA=True,
                    removeNAhow="any",
                    runRemoveOutliers=True,
                    sd_val=3,
                    runRemoveOutOfBound=True,
                    low_bound=0,
                    high_bound=9998,
                    runExtendIndex=False):
        
        logging.info("Flagging data")

        data = self.data_raw
                    
        if runRemoveNA:
            
            try:
                self.flagNA(data, removeNAhow)
                selector = self.droppedNA
                
                logging.info("_dataset NA flagged")
            except:
                pass
            
        if runRemoveOutliers:
            
            # sd_val=3
            try:
                self.flagOutlier(data, sd_val)
                selector = selector | self.droppedOutliers
                
                logging.info("_outliers flagged")

            except:
                pass

        if runRemoveOutOfBound:
            
            # low_bound=0
            # high_bound=9998
            try:

                self.flagOutOfBound(data, low_bound, high_bound)
                selector = selector | self.droppedOutOfBound
                
                logging.info("_outOfBound points flagged")

            except:
                pass
        
        self.data_removed = self.data_raw[selector]

        return self.data_removed


    def flag_outliers(self, data, sd_val):
        data = data.dropna()
        self.droppedOutliers = pd.Series(
            (~(np.abs(stats.zscore(data)) < float(sd_val)).all(axis=1)), index=data.index)

        return

    def flag_out_of_bound(self, data, low_bound, high_bound):
        data = data.dropna()
        self.droppedOutOfBound = ~((data > low_bound).all(
            axis=1) & (data < high_bound).all(axis=1))

    def count_na(self, data):
        return data.isnull().sum()

    def count_constants(self, data):
        """counts the % of points in each TS that does not change"""
        return (data.diff() == 0).sum() / data.shape[0] * 100

    def add_time_features(self, data):
        data["YEAR"] = data.index.year
        data["MONTH"] = data.index.month
        data["TOD"] = data.index.hour
        data["DOW"] = data.index.weekday
        data["WEEK"] = data.index.week
        data["DOY"] = data.index.dayofyear

        self.data_preprocessed = data
        return data

    def add_degree_days(self, data, hdh_cpoint=65, cdh_cpoint=65):

        data["hdh"] = data["OAT"]
        over_hdh = data.loc[:, "OAT"] > hdh_cpoint
        data.loc[over_hdh, "hdh"] = 0
        data.loc[~over_hdh, "hdh"] = hdh_cpoint - data.loc[~over_hdh, "OAT"]

        data["cdh"] = data["OAT"]
        under_cdh = data.loc[:, "OAT"] < cdh_cpoint
        data.loc[under_cdh, "cdh"] = 0
        data.loc[~under_cdh, "cdh"] = data.loc[~under_cdh, "OAT"] - cdh_cpoint

        self.data_preprocessed = data
        return

    def create_dummies(self, data, var_to_expand=["TOD", "DOW"]):
        for var in var_to_expand:
            add_var = pd.get_dummies(data[var], prefix=var)
            data = data.join(add_var)  # add all the columns to the model data

        self.data_preprocessed = data
