'''
This class preprocess and clean data

@author Marco Pritoni <marco.pritoni@gmail.com>
latest update: Feb 14 2017 

TODO:

-think about best way of interpolating/resampling (1-groupby TimeGrouper, resample, interpolate)
-save the list of point removed
-add preprocessing as in mave (data noramlization around 0)

version 0.1
'''

import pandas as pd
from scipy import stats
import numpy as np


class data_preprocessor(object):
    "preproccessor class for data cleaning and manipulation (standardization for machine learning)"
    
    def __init__(self, 

                    df, 

                    runInterpolate=True,
                   
                    runRemoveNA=True,
                   
                    runRemoveOutliers=True,
                   
                    runRemoveOutOfBound=True,
                   
                    runResample=True,
                   
                    runExtendIndex=False,
                   
                    time_res="h",
                   
                    sd_val=3,
                   
                    low_bound=0,
                   
                    high_bound=9998,
                   
                    freq="h",

                    *args, 

                    **kw):
        
        self.data_raw=df
        
        self.data_cleaned=self.clean_data(df,
                                runInterpolate,
                   
                                runRemoveNA,
                   
                                runRemoveOutliers,
                   
                                runRemoveOutOfBound,
                   
                                runResample,
                   
                                runExtendIndex,
                   
                                time_res,
                   
                                sd_val,
                   
                                low_bound,
                   
                                high_bound,
                   
                                freq)
    

    def interpolateData(self, 
                        data,
                        time_res,
                        ):

        data=data.groupby(pd.TimeGrouper(time_res)).mean()
        # may want to look into resample() or interpolate() method alternatively 
        
        return data


    def removeNA(self,
                 data
                 ):
        
        return data.dropna()

    
    def removeOutliers(self,
                       data,
                       sd_val
                       ):

        # this removes all data data above or below n  sd_val from the mean
        # this also excludes all lines with NA in any column
        

        data=data.dropna()[(np.abs(stats.zscore(data.dropna())) < float(sd_val)).all(axis=1)]

        return data

    def removeOutOfBound(self,
                            data,
                            low_bound,
                            high_bound
                            ):
        
        data=data.dropna()
        data=data[(data >low_bound).all(axis=1) & (data <high_bound).all(axis=1)]


        return data

    def resampleData(self,
                     data,
                     freq
                       ):
        
            
        return data.resample(freq).mean()

    
    def extendIndex(self,
                       ):
        
        return
 
    def clean_data(self, 

                   data,

                   runInterpolate=True,
                   
                   runRemoveNA=True,
                   
                   runRemoveOutliers=True,
                   
                   runRemoveOutOfBound=True,
                   
                   runResample=True,
                   
                   runExtendIndex=False,
                   
                   time_res="h",
                   
                   sd_val=3,
                   
                   low_bound=0,
                   
                   high_bound=9998,
                   
                   freq="h"
                                                 
                   ):
        
        # save the instance of the DataSet(DataFrame) in a local variable
        # this allows to use DataSet methods such as data.interpolate()
        
        #data=self
        print "debugging"
        
        # apply these methods with this sequence
        
        if runInterpolate:
            
            #time_res="h"
            try:
                data=self.interpolateData(data,time_res)
                
                print "_interpolate works"
            except:
                pass
            
        if runRemoveNA:
            
            try:
                data=self.removeNA(data)
                                
                print "_removeNA works"
            except:
                pass
            
        if runRemoveOutliers:
            
            #sd_val=3
            try:

                data=self.removeOutliers(data, sd_val)
                print "_removeOutliers works"

            except:
                pass

        if runRemoveOutOfBound:
            
            #low_bound=0
            #high_bound=9998
            try:

                data=self.removeOutOfBound(data, low_bound,high_bound)
                print "_removeOutOfBound works"

            except:
                pass
            
        if runResample:
            
            #freq="d"
            try:

                data=self.resampleData(data, freq)
                print "_resampleData works"

            except:
                pass
            
        if runExtendIndex:
        
            try:
                print "testing"
            except:
                pass
            

        return data

    def feature_extraction(self,data):
        data["YEAR"]=data.index.year
        data["MONTH"]=data.index.month
        data["TOD"]=data.index.hour
        data["DOW"]=data.index.weekday
        data["WEEK"]=data.index.week
        data["DOY"]=data.index.dayofyear

        return


    