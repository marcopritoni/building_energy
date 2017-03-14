'''
This class preprocess and clean data

Assumptions:

Input: Dataframe of TS

Output: ?



TODO:
-- general:
- comment code 

-- data cleaning:
- add a resample at the end 
- more sophisticated outlier removal see here: https://ocefpaf.github.io/python4oceanographers/blog/2015/03/16/outlier_detection/
- replace NA/outliers with mean/median instead ... .fillna

-- data cleaning fundamentals:
- verify data types in case of non num values (more of a problem when reading csv)
- remove duplicates
- find patterns? Whether it is simple search/replace rules, regular expressions, pattern matching 
or completely custom transformations ???
- deal with time zone: 


-- preprocessing:
-add preprocessing as in mave (data noramlization around 0)
-need to make sure this works with power (instantaneous) and energy (summation in period) and cumulative energy (cumsum)
-add a flag if series not sationary : https://www.analyticsvidhya.com/blog/2016/02/time-series-forecasting-codes-python/
http://machinelearningmastery.com/time-series-data-stationary-python/
- idenfify start/end of data missing and const values

-- functional interface:
-figure out calls/inputs/outputs

@author Marco Pritoni <marco.pritoni@gmail.com>
latest update: Feb 19 2017 

version 0.3
'''

import pandas as pd
from scipy import stats
import numpy as np


class data_preprocessor(object):
    "preproccessor class for data cleaning and manipulation (standardization for machine learning)"
    
    def __init__(self, 

                    df, 

                    runResample=True,

                    freq="h",                   

                    runInterpolate=True,

                    limit=1,
                   
                    runRemoveNA=True,
                    
                    removeNAhow='any',
                    
                    runRemoveOutliers=True,

                    sd_val=3,
                   
                    runRemoveOutOfBound=True,
                   
                    low_bound=0,
                   
                    high_bound=9998,       

                    *args, 

                    **kw):
        
        self.data_raw=df

        self.data_cleaned=df

        self.data_removed=pd.DataFrame()
        
        self.data_preprocessed=pd.DataFrame()

        self.droppedNA=pd.Series()
        
        self.droppedOutliers=pd.Series()
        
        self.droppedOutOfBound=pd.Series()
    

    def resampleData(self,
                     data,
                     freq
                       ):
            
        data=data.resample(freq).mean()

        return data
        # also need to deal with energy quantities where resampling is .sum()
        # figure out how to apply different functions to different columns .apply( )
        # this theoretically work in upsampling too, check docs
        # http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.resample.html 
   

    def interpolateData(self, 
                        data,
                        limit
                        ):

        data=data.interpolate(how="index", limit=limit)
         
        return data


    def removeNA(self,
                 data,
                 removeNAhow,
                 ):
        
        return data.dropna(how=removeNAhow)

    
    def removeOutliers(self,
                       data,
                       sd_val
                       ):

        # this removes all data data above or below n  sd_val from the mean
        # this also excludes all lines with NA in any column
        data=data.dropna()
        data=data[(np.abs(stats.zscore(data)) < float(sd_val)).all(axis=1)]
        
        # should do this with a moving windows
 
        return data


    def removeOutOfBound(self,
                            data,
                            low_bound,
                            high_bound
                            ):
        
        data=data.dropna()
        data=data[(data >low_bound).all(axis=1) & (data <high_bound).all(axis=1)]
        # this may need a different boundary for each column

        return data

     
    def flagNA(self,
                 data,
                 removeNAhow):
        
        if removeNAhow=="any":
            
            self.droppedNA=data.isnull().any(axis=1)
        
        elif removeNAhow=="all":
            
            self.droppedNA=data.isnull().all(axis=1)
            
        return

    
    def flagOutlier(self,
                 data,
                 sd_val):
        
        data=data.dropna()
        
        self.droppedOutliers= pd.Series((~(np.abs(stats.zscore(data)) < float(sd_val)).all(axis=1)),index=data.index)
            
        return

    
    def flagOutOfBound(self,
                 data,
                 low_bound,
                 high_bound
                      ):
        
        data=data.dropna()
        
        self.droppedOutOfBound= ~((data >low_bound).all(axis=1) & (data <high_bound).all(axis=1))
        return


    def countNA ( self,
                 data):
        
        return data.isnull().sum()
        
    def countConstant ( self,
                 data):
        #this function counts what is the % of points in each TS that does not chanve 
        return (data.diff()==0).sum()/data.shape[0]*100    
    
    
    def clean_data(self, 

                    runResample=True,

                    freq="h",                   

                    runInterpolate=True,

                    limit=1,
                   
                    runRemoveNA=True,
                   
                    removeNAhow='any',
                    
                    runRemoveOutliers=True,

                    sd_val=3,
                   
                    runRemoveOutOfBound=True,
                   
                    low_bound=0,
                   
                    high_bound=9998
                  ):

        
        # save the instance of the DataSet(DataFrame) in a local variable
        # this allows to use DataSet methods such as data.interpolate()
        
        print "debugging clean_data"
        
        # apply these methods with this sequence

        data=self.data_raw
        
        if runResample:
            
            #freq="d"
            try:

                data=self.resampleData(data, freq)
                print "_dataset resampled at %s" %freq

            except:
                pass

        if runInterpolate:
            
            #time_res="h"
            try:
                data=self.interpolateData(data,limit=limit)
                
                print "_dataset interpolated with limit of %s element" %limit
            except:
                pass
            
        if runRemoveNA:
            
            try:
                data=self.removeNA(data, removeNAhow)
                                
                print "_dataset NA removed"
            except:
                pass
            
        if runRemoveOutliers:
            
            #sd_val=3
            try:

                data=self.removeOutliers(data, sd_val)
                print "_outliers removed"

            except:
                pass

        if runRemoveOutOfBound:
            
            #low_bound=0
            #high_bound=9998
            try:

                data=self.removeOutOfBound(data, low_bound,high_bound)
                print "_outOfBound points removed"

            except:
                pass
            
                      

        self.data_cleaned=data

        return data

    
    def flag_data(self, 
                   
                    runRemoveNA=True,
                   
                    removeNAhow='any',
                    
                    runRemoveOutliers=True,

                    sd_val=3,
                   
                    runRemoveOutOfBound=True,
                   
                    low_bound=0,
                   
                    high_bound=9998,

                    runExtendIndex=False ):
        
        print "debugging flag_data"
        
        # apply these methods with this sequence

        data=self.data_raw
                    
        if runRemoveNA:
            
            try:
                self.flagNA(data, removeNAhow)
                selector=self.droppedNA
                
                print "_dataset NA flagged"
            except:
                pass
            
        if runRemoveOutliers:
            
            #sd_val=3
            try:
                self.flagOutlier(data, sd_val)
                selector=selector | self.droppedOutliers
                
                print "_outliers flagged"

            except:
                pass

        if runRemoveOutOfBound:
            
            #low_bound=0
            #high_bound=9998
            try:

                self.flagOutOfBound(data, low_bound,high_bound)
                selector=selector | self.droppedOutOfBound
                
                print "_outOfBound points flagged"

            except:
                pass
        
        self.data_removed=self.data_raw[selector]

        return self.data_removed
    
    
    def add_timeFeatures (self,
                          data):
        
        data["YEAR"]=data.index.year
        data["MONTH"]=data.index.month
        data["TOD"]=data.index.hour
        data["DOW"]=data.index.weekday
        data["WEEK"]=data.index.week
        data["DOY"]=data.index.dayofyear

        self.data_preprocessed=data

        return data

    def add_degreeDays (self,
                        data, 
                        hdh_cpoint=65, 
                        cdh_cpoint=65):
    
        data['hdh'] = data['OAT']
        over_hdh = data.loc[:,'OAT'] > hdh_cpoint
        data.loc[over_hdh,'hdh'] = 0 
        data.loc[~over_hdh,'hdh'] = hdh_cpoint-data.loc[~over_hdh,'OAT']
        
        data['cdh'] = data['OAT']
        under_cdh = data.loc[:,'OAT'] < cdh_cpoint
        data.loc[under_cdh,'cdh']=0
        data.loc[~under_cdh,'cdh']=data.loc[~under_cdh,'OAT']-cdh_cpoint
    
        self.data_preprocessed=data
        
        return
        
    def create_dummies (self,
                       data,
                       var_to_expand=["TOD","DOW"]
                       ):
    
        for var in var_to_expand:
            add_var=pd.get_dummies(data[var],prefix=var)
            data=data.join(add_var) # add all the columns to the model data

        self.data_preprocessed=data

        return
    