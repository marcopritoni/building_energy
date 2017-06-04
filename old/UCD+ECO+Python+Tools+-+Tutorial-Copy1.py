
# coding: utf-8

# # UCD ECO Python Tools - Tutorial

# In[2]:

import pandas as pd
import os
import requests as req
import json
import numpy as np
import datetime

from matplotlib import style
import matplotlib
get_ipython().magic(u'matplotlib inline')
style.use('ggplot')

#  new modules - marco.pritoni@gmail.com
from PIPy_Datalink import *
from Data_Preprocessor import *


# ## PI datalink - Python implementation

# In[3]:

p=pipy_datalink()


# In[4]:

## method get_stream()
## get the stream by WebID
## input: Web ID
## 
## output: pandas DataFrame/dictionary
##
## arguments: 
## Web_ID=None : - the unique identifier of the time series 
## _start="y" : - start date, default yesterday "y"; can use different formats as "YYYY-MM-DD";
## _end="t" : - end date, default yesterday "t"; can use different formats as "YYYY-MM-DD";        
## _calculation="interpolated": can use "recorded" to get raw data and summary to get summary data (tot, mean, sd);
## note: summary data is not a time series, but a dictionary
## _interval="1h": interpolation interval, used only with interpolated; default 1 hour
## _controller=None : not used at the moment; needed for future extensions 
#  _sumType=None : used if calculation is "summary", can use All, Total, default Total
#  _label=None : not used at the moment; needed for future extensions 

Web_ID="A0EbgZy4oKQ9kiBiZJTW7eugwNFN9S7KS5BG0-xgDcyrprwDXFgAtlASVonZNgP17EChQVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdTXFBMQU5UICYgRU5WSVJPTk1FTlRBTCBTQ0lFTkNFU1xFTEVDVFJJQ0lUWXxERU1BTkRfS0JUVQ"

# plot and show results
p.get_stream(Web_ID,_start="2016-01-22", _end="2017-01-24", _label="UnknownName").plot(figsize=(16,5), legend=False)
p.get_stream(Web_ID,_start="2016-01-22", _end="2017-01-24",_label="UnknownName").head()


# In[5]:

## example using the _calculation="summary"
Web_ID="A0EbgZy4oKQ9kiBiZJTW7eugwNFN9S7KS5BG0-xgDcyrprwDXFgAtlASVonZNgP17EChQVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdTXFBMQU5UICYgRU5WSVJPTk1FTlRBTCBTQ0lFTkNFU1xFTEVDVFJJQ0lUWXxERU1BTkRfS0JUVQ"

# plot and show results
p.get_stream(Web_ID,_start="2017-01-22", _end="2017-01-24", _calculation="summary",_sumType="All",_label="UnknownName")


# In[6]:

## get_stream_by_point()
##
## getting the data by WebIDs is not pratical
## we want to get the data by data point name 
## 
## input: point name; can use *  
##
## output: pandas DataFrame/dictionary
##
##
## arguments: 
## point_name : - the name is unique in each database 
## _start="y" : - start date, default yesterday "y"; can use different formats as "YYYY-MM-DD";
## _end="t" : - end date, default yesterday "t"; can use different formats as "YYYY-MM-DD";        
## _calculation="interpolated": can use "recorded" to get raw data and summary to get summary data (tot, mean, sd);
## note: summary data is not a time series, but a dictionary
## _interval="1h": interpolation interval, used only with interpolated; default 1 hour
## _controller=None : not used at the moment; needed for future extensions 
#  _sumType=None : used if calculation is "summary", can use All, Total, default Total
#  _label=None : not used at the moment; needed for future extensions 
# dataserver : there can be more databases in a PI environment; default "s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q"

point_name="Ghausi.AHU01.RM1113:ROOM.TEMP"

p.get_stream_by_point(point_name).plot(figsize=(16,5))


# In[7]:

# test this with multiple point names

point_nm=["Ghausi.AHU01.RM1113:ROOM.TEMP","Ghausi.AHU01.RM1113:ROOM.DAT"]

p.get_stream_by_point(point_nm).plot(figsize=(16,5))
p.get_stream_by_point(point_nm).head()


# In[8]:

# show that also the summary works for multiple columns
p.get_stream_by_point(point_nm,_start="2017-01-22", _end="2017-01-24", _calculation="summary",_sumType="All",_label="UnknownName")


# In[9]:

# test of calculatio _end
point_nm=["Ghausi.AHU01.RM1113:ROOM.TEMP","Ghausi.AHU01.RM1113:ROOM.DAT"]

p.get_stream_by_point(point_nm,_start="2017-01-22", _end="2017-01-24", _calculation="end",_sumType="All",_label="UnknownName")


# In[10]:

## search_by_point()
## method to search for data points names using * 
##
## output: list of point names and dictionary of point name: WebIDs

l, d = p.search_by_point("OAT")
l


# In[11]:

d


# ## Clean Data 

# In[12]:

# find meters at Ghausi Hall
p.search_by_point("Ghausi*BTU")


# In[13]:

# select all three meters and plot them;  clearly see the outliers
point_names= ['Ghausi_ChilledWater_Demand_kBtu','Ghausi_Electricity_Demand_kBtu','Ghausi_Steam_Demand_kBtu']
dr=p.get_stream_by_point(point_names,_start="2016-01-22", _end="2016-03-15")
dr.plot(figsize=(18,5))

#show data before the spike
tSlicer=(slice("2016-01","2016-02-25"))

dr.loc[tSlicer,:].plot(figsize=(18,5))


# In[14]:

# run the data through data cleaning (all default inputs)
dp=data_preprocessor(dr)
tSlicer=(slice(None))
dp.data_cleaned.loc[tSlicer,:].plot(figsize=(18,5))


# In[15]:

# run the data through data cleaning (can also choose options)
dp=data_preprocessor(dr,
                    
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
tSlicer=(slice(None))

dp.data_cleaned.loc[tSlicer,:].plot(figsize=(18,5))


# In[16]:

down=pipy_datalink()


# In[17]:

temp= down.get_stream_by_point(['Ghausi_Electricity_Demand_kBtu','OAT'],_start="2014",_end="t")#.plot()


# In[18]:

temp.plot()


# In[19]:

dp=data_preprocessor(temp,
                    
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


# In[20]:

dp.data_cleaned.plot()


# In[26]:

# 1 filter data periods
# 2 separate datasets
# 3 separate output and input
# 4 train a model
# 5 get scores for the model = validation
# 6 predict
# 7 compare 

from sklearn import svm, cross_validation, linear_model, preprocessing, ensemble
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error


# In[30]:

#1-3
tSlicer=(slice("2014-01","2014-12"))

var= 'Ghausi_Electricity_Demand_kBtu'
values = dp.data_cleaned.loc[tSlicer,var].values
values.reshape(-1, 1)


# In[31]:

#4
mod = linear_model.LinearRegression()  
model_coeff = mod.fit(values, values) # output, input in np arrays


# In[ ]:

#5 model.score(data_train,target_train) same data for training


# In[ ]:

#6
model_coeff.predict() # input period 2


# In[ ]:

# compare
# real period2 var vs predicted with regression (#6)

