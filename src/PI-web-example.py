
# coding: utf-8

# In[18]:

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

#  new class - marco.pritoni@gmail.com
from PI_downloader import *


# In[19]:

# instantiate the class
p = PI_stream_downloader()


# In[20]:

# method get_stream()
# get the stream by WebID
# input: Web ID
##
# output: pandas Series/dictionary
##
# arguments:
# Web_ID=None : - the unique identifier of the time series
# _start="y" : - start date, default yesterday "y"; can use different formats as "YYYY-MM-DD";
# _end="t" : - end date, default yesterday "t"; can use different formats as "YYYY-MM-DD";
# _calculation="interpolated": can use "recorded" to get raw data and summary to get summary data (tot, mean, sd);
# note: summary data is not a time series, but a dictionary
# _interval="1h": interpolation interval, used only with interpolated; default 1 hour
# _controller=None : not used at the moment; needed for future extensions
#  _sumType=None : used if calculation is "summary", can use All, Total, default Total
#  _label=None : not used at the moment; needed for future extensions

Web_ID = "A0EbgZy4oKQ9kiBiZJTW7eugwNFN9S7KS5BG0-xgDcyrprwDXFgAtlASVonZNgP17EChQVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdTXFBMQU5UICYgRU5WSVJPTk1FTlRBTCBTQ0lFTkNFU1xFTEVDVFJJQ0lUWXxERU1BTkRfS0JUVQ"

# plot and show results
p.get_stream(Web_ID, _start="2017-01-22",
             _end="2017-01-24").plot(figsize=(16, 5))
p.get_stream(Web_ID)


# In[21]:

# example using the _calculation="summary"
Web_ID = "A0EbgZy4oKQ9kiBiZJTW7eugwNFN9S7KS5BG0-xgDcyrprwDXFgAtlASVonZNgP17EChQVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdTXFBMQU5UICYgRU5WSVJPTk1FTlRBTCBTQ0lFTkNFU1xFTEVDVFJJQ0lUWXxERU1BTkRfS0JUVQ"

# plot and show results
p.get_stream(Web_ID, _start="2017-01-22", _end="2017-01-24",
             _calculation="summary", _sumType="All")


# In[22]:

# get_stream_by_point()
##
# getting the data by WebIDs is not pratical
# we want to get the data by data point name
##
# input: point name; can use *
##
# output: pandas Series/dictionary
##
##
# arguments:
# point_name : - the name is unique in each database
# _start="y" : - start date, default yesterday "y"; can use different formats as "YYYY-MM-DD";
# _end="t" : - end date, default yesterday "t"; can use different formats as "YYYY-MM-DD";
# _calculation="interpolated": can use "recorded" to get raw data and summary to get summary data (tot, mean, sd);
# note: summary data is not a time series, but a dictionary
# _interval="1h": interpolation interval, used only with interpolated; default 1 hour
# _controller=None : not used at the moment; needed for future extensions
#  _sumType=None : used if calculation is "summary", can use All, Total, default Total
#  _label=None : not used at the moment; needed for future extensions
# dataserver : there can be more databases in a PI environment; default
# "s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q"

point_name = "Ghausi.AHU01.RM1113:ROOM.TEMP"

p.get_stream_by_point(point_name).plot(figsize=(16, 5))
p.get_stream_by_point(point_name)


# In[23]:

# search_by_point()
# method to search for data points names using *
##
# output: list of point names and dictionary of point name: WebIDs

l, d = p.search_by_point("GHAUSI*AHU01*RM1113*")


# In[24]:

l


# In[25]:

d


# In[ ]:


# In[ ]:
