
# new version - removed multi-streams and table stuff from get_PI_stream. now it requires single webID


import pandas as pd
import os
import requests as req
import json
import numpy as np

class PI_stream_downloader(object):
    
    def __init__(self, root=None,calculation=None, interval=None, buildingMeterDB=None):
        
        if root==None:
            self.root="https://ucd-pi-iis.ou.ad3.ucdavis.edu/piwebapi/"

    def search_by_point (self,
                        point_query,
                        dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q",
                        include_WebID=True,
                        ):
        # compose url
        point_search="/points?nameFilter="
        query_string=self.root+"dataservers/"+dataserver+point_search+point_query
        parms={"startIndex":0,"maxCount":100000,"selectedFields": "Items.WebId;Items.Name"}
        
        # call request library
        response=req.get(query_string, parms)
        
        # parse the response
        js=json.loads(response.text)
        
        # save results in a list of points and a dict of {point_name: Web_ID}
        point_list=[]
        point_dic={}
        
        for elem in range(0, len (js["Items"])):
            Point_name_full=js["Items"][elem]["Name"]
            point_list.append(Point_name_full)

            # can also return dict 
            if include_WebID:
                Web_ID_=js["Items"][elem]["WebId"]
                point_dic[Point_name_full]=Web_ID_

        try:
            return point_list, point_dic
        except:
            return point_list, point_dic
            
    def get_webID_by_point (self, 
                               point_name,
                               dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q"  # defaults to buildings dataserver
                              ):

        pointList, PointDic=self.search_by_point(point_name, include_WebID=True)
        
        if len (pointList)>1:
            print "warining: the query returned more than one WebID n=%d, \
            only the first one is used\n returning only first" %len (pointList)
        Web_ID_=PointDic[pointList[0]]

        print Web_ID_
        return Web_ID_

    
    def get_stream_by_point (self,
                                 point_name,
                                _start="y", 
                                _end="t", 
                                _calculation="interpolated",
                                _interval="1h",
                                _controller=None,
                                _sumType=None,
                                _label=None,
                                dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q",  # defaults to buildings dataserver
                                ):                                    
                            
        Web_ID=self.get_webID_by_point(point_name,dataserver)
        stream=self.get_stream(Web_ID,_start,_end,_calculation, _interval, _controller, _sumType, _label)

        return stream
    
### This is the fundamental function that gets the stream and returns a pandas Series or summary dic or single value
### when _calculation is "interpolated" or "recorded" it returns a series
### when _calculation is "summary" it returns a dic with different summary metrics : values
### when _calculation is "end" it returns a single value, the last one
### When it returns a ts, it inherits all the nice methods and properties like .plot()
    
    
    def get_stream (self, Web_ID=None, 
                      _start="y", 
                      _end="t", 
                      _calculation="interpolated",
                      _interval="1h",
                      _controller=None,
                      _sumType=None,
                      _label=None):        
       
        # call function that constructs the http call for method /streams (see PI API manual for API details)
        response=self._compose_stream_url(Web_ID,_start,_end,_calculation,_interval,_controller, _sumType, _label)

        # prints for testing: <Response [200]> means it works
        print response

        # parse the response
        if _calculation == (("interpolated") or ("recorded")):            
            result=self._parse_TS(response,Web_ID,_label)
        elif _calculation == ("summary"):
            result=self._parse_summary(response,_label)
        elif _calculation == ("end"):
            result=self._parse_end(response,_label)

        return result
        
    def _compose_stream_url (self, Web_ID, 
                        _start, 
                        _end, 
                        _calculation,
                        _interval,
                        _controller,
                        _sumType,
                        _label):          

        # constructs the first part of the http call 
        Web_ID_string=self.root+"streams/"+Web_ID+"/"+_calculation
        print Web_ID_string
        
        # constructs the parameters for requests REST api call
        if _sumType:
            parms={"startTime":_start,"endTime": _end,"interval":_interval, "summaryType":_sumType}
        else:
            parms={"startTime":_start,"endTime": _end,"interval":_interval}
          
        # call python library for json/http REST API
        response=req.get(Web_ID_string, parms)
        return response
    
    def _parse_TS(self, response, Web_ID,_label):
        if response:
            # loads content of json response
            js=json.loads(response.text)

            timeseries={}
            # counts the elements
            n_elem =len(js["Items"])
        
            # loops through the json in search of timestep and value - note this is not vectorized as the structure is irregular
            for i in range (0, n_elem):
                
                # saves timestep 
                timestamp=js["Items"][i]["Timestamp"]
                
                # saves value - unless the calculated value is missing (failed calculation)
                value=js["Items"][i]["Value"]
                try:
                    # format to float
                    float(value)
                    pass
                except:
                    # if calculation failed can ignore the results (nan)
                    value=np.nan
                    # or can get the default value: fixed
                    #value=js["Items"][i]["Value"]["Value"]

                # saves timeseries and value in a dictionary
                timeseries[timestamp]= value

            # converts dict into pandas series
            ts=pd.Series(timeseries)
            
            # converts Series index to datetime type
            ts.index=pd.to_datetime(ts.index)
            
            # saves name of the Series
            if _label:
                
                # uses lable provided 
                ts.name=_label
            else:
                
                # uses the WebID if label not provided
                ts.name=Web_ID
        
        # If the requests fails
        else:
            # print to screen error
            print "I can't find the stream with this WebID"
            # returns empty time series
            return pd.Series()
        return ts  

    def _parse_summary(self, response, _label):
        if response:
            # loads content of json response
            js=json.loads(response.text)
 
            # counts the elements
            n_elem =len(js["Items"])
            summary_dic={}
            # print js["Items"] # print to test
            # loops through the json to extract each summary value
            for i in range (0, n_elem):
                sumType=js["Items"][i][u'Type']
                SumVal=js["Items"][i][u'Value'][u'Value']
                summary_dic[sumType]=SumVal
             
            # print summary_dic #print to test 
        else:
            # print error to screen
            print "I can't find the stream with this WebID"
        return summary_dic
    
    def _parse_end(self, response, _label):
        if response:
            # loads content of json response
            js=json.loads(response.text)

            print js
        else:
            # print to screen error
            print "I can't find the stream with this WebID"

        return js[u'Value']