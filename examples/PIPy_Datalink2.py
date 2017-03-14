
'''
This class is a wrapper for PI web API

It replicates the functions of PI datalink excel Add-on (Windows only) in Python

Some features may be UC Davis specific, but can easily be extended to other PI installations

v0.5
-reorganized code: help methods first
-added path search - this actually requires four different methods to parse the object returned because they are different than the serach by point
(get_stream_by_path, get_webID_by_path, search_by_path, _parse_path)

v0.4
-calculation default to _sumType=All
-removed the printing statement of point name and webID

v0.3
-returns DataFrame for all get options
-added a method to parse names

v0.1 
-renamed PI_downloader to PIPy_Datalink (similar to the excel plugin)

BUGS:
-when using _labels arg, path should return the column with _label name

@author Marco Pritoni <marco.pritoni@gmail.com>
@author + EEC Project 3 team

latest update: Feb 28 2017 

'''

import pandas as pd
import os
import requests as req
import json
import numpy as np

class pipy_datalink(object):
    
    def __init__(self, root=None,calculation=None, interval=None, buildingMeterDB=None):
        
        if root==None:
            
            # for more general application this root should be read from config file in not set as an arg
            self.root="https://ucd-pi-iis.ou.ad3.ucdavis.edu/piwebapi/"


    def _parse_point(self,response,include_WebID):
        """
        Example API json returned:

        {
          "Items": [
            {
              "WebId": "P09KoOKByvc0-uxyvoTV1UfQ61oCAAVVRJTC1QSS1QXFBFUy5BSFUuQ09PTElORyBFTkVSR1kgQlRVIFBFUiBIUg",
              "Name": "PES.AHU.Cooling Energy BTU per Hr"
            },
            {
              "WebId": "P09KoOKByvc0-uxyvoTV1UfQ7FoCAAVVRJTC1QSS1QXFBFUy5BSFUuSEVBVElORyBFTkVSR1kgQlRVIFBFUiBIUg",
              "Name": "PES.AHU.Heating Energy BTU per Hr"
            }
        }
        """

        js=json.loads(response.text)
        
        # save results in a list of points and a dict of {point_name: Web_ID}
        point_list=[]
        point_dic={}

        # PARSE what is returned 
        for elem in range(0, len (js["Items"])): # for each element in the json structure

            Point_name_full=js["Items"][elem]["Name"] # see example 
            point_list.append(Point_name_full)

            # can also return dict 
            if include_WebID:
                Web_ID_=js["Items"][elem]["WebId"]
                point_dic[Point_name_full]=Web_ID_

        try:
            return point_list, point_dic
        except:
            return point_list, point_dic


    def _parse_path(self,response,include_WebID):
        """
        Example API json returned:


        {
          "WebId": "A0EbgZy4oKQ9kiBiZJTW7eugwS5GAMtE55BGIPhgDcyrprwcrOde7rrSVobodgP17EChQVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdTXFJJRkxFIFJBTkdFXEVMRUNUUklDSVRZfERFTUFORF9LQlRV",
          "Name": "Demand_kBtu"
        }

        NOTE: this is different from the JSON obtained by search_by_point
        Only single WebId and Name are returned in response. Parsing accordingly.
        Kept variable names same as _parse_point. Did not need to update since only used in local context.
        """

        js=json.loads(response.text)
        
        # save results in a list of points and a dict of {point_name: Web_ID}
        point_list=[]
        point_dic={}

        # PARSE what is returned 

        Point_name_full=js["Name"] # Have yet to encounter multiple return Items so removed for_loop indexing
        point_list.append(Point_name_full)

        # can also return dict 
        if include_WebID:
            Web_ID_=js["WebId"]
            point_dic[Point_name_full]=Web_ID_

        try:
            return point_list, point_dic
        except:
            return point_list, point_dic    


    def _parse_TS(self, response, Web_ID,_label):
        """
        Example API json parsed:

        {
          "Links": {},
          "Items": [
            {
              "Timestamp": "2017-02-10T02:45:00.2475263Z",
              "Value": 75.20761,
              "UnitsAbbreviation": "",
              "Good": true,
              "Questionable": false,
              "Substituted": false
            },
            {
              "Timestamp": "2017-02-10T03:45:00.2475263Z",
              "Value": 75.19933,
              "UnitsAbbreviation": "",
              "Good": true,
              "Questionable": false,
              "Substituted": false
            }
        }
        """
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
            ts=pd.DataFrame(ts)
        
        # If the requests fails
        else:
            # print to screen error
            print "I can't find the stream with this WebID"
            
            # returns empty Dataframe
            return pd.DataFrame()
            
        
        return ts  


    def _parse_summary(self, response, Web_ID, _label):
        """
        Example API json parsed:

        {
          "Links": {},
          "Items": [
            {
              "Type": "Total",
              "Value": {
                "Timestamp": "2017-02-10T04:09:00.7909406Z",
                "Value": 75.166832186264742,
                "UnitsAbbreviation": "",
                "Good": true,
                "Questionable": false,
                "Substituted": false
              }
            },
            {
              "Type": "Average",
              "Value": {
                "Timestamp": "2017-02-10T04:09:00.7909406Z",
                "Value": 75.166832186264742,
                "UnitsAbbreviation": "",
                "Good": true,
                "Questionable": false,
                "Substituted": false
              }
            },
         ....
        """
        if response:
            # loads content of json response
            js=json.loads(response.text)
 
            # counts the elements
            n_elem =len(js["Items"])
            summary_dic={}
            # print js["Items"] # print to test
            # loops through the json to extract each summary value
            for i in range (0, n_elem):
                sumType=js["Items"][i]['Type']
                SumVal=js["Items"][i]['Value']['Value']
                summary_dic[sumType]=SumVal

            df_summ=pd.DataFrame.from_dict(summary_dic,orient='index')

            if _label:
                df_summ.columns=[_label]

            else:
                df_summ.columns=[Web_ID]

            return df_summ

        else:
            # print error to screen
            print "I can't find the stream with this WebID"
        return pd.DataFrame()


    def _parse_end(self, response, Web_ID, _label):
        """
        Example API json parsed:
        {
          "Timestamp": "2017-02-10T07:59:00Z",
          "Value": 75.1643,
          "UnitsAbbreviation": "",
          "Good": true,
          "Questionable": false,
          "Substituted": false
        }

        """  
        if response:
            # loads content of json response
            js=json.loads(response.text)

            end_dic={}

            # save json object in a dictionary
            end_dic['Good']=js['Good']
            end_dic['Timestamp']=js['Timestamp']
            end_dic['Value']=js['Value']

            df_end=pd.DataFrame.from_dict(end_dic,orient='index')

            if _label:
                df_end.columns=[_label]

            else:
                df_end.columns=[Web_ID]

            return df_end


        else:
            # print to screen error
            print "I can't find the stream with this WebID"

        return js['Value']


    def _compose_stream_url (self, Web_ID, 
                        _start, 
                        _end, 
                        _calculation,
                        _interval,
                        _sumType,
                        _label):        
        """
        This method composes the url to get the stream
        """  

        # constructs the first part of the http call 
        Web_ID_string=self.root+"streams/"+Web_ID+"/"+_calculation
#        print Web_ID_string
        
        # constructs the parameters for requests REST api call
        if _sumType:
            parms={"startTime":_start,"endTime": _end,"interval":_interval, "summaryType":_sumType}
        else:
            parms={"startTime":_start,"endTime": _end,"interval":_interval}
          
        # call python library for json/http REST API
        response=req.get(Web_ID_string, parms)
        return response

    
    def search_by_point (self,
                        point_query,
                        dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q",
                        include_WebID=True,
                        ):
        """ 
        This method searches for points allowing * operators. It returns point list and a Dictionary with names:WebIDs
        
        arguments:

        point_query: point name expression (allows *)
        dataserver: default point to UC Davis
        include_WebID: by default True, ut returns list AND a dictionary {name : Web_ID, ...}


        Example API json returned:

        {
          "Items": [
            {
              "WebId": "P09KoOKByvc0-uxyvoTV1UfQ61oCAAVVRJTC1QSS1QXFBFUy5BSFUuQ09PTElORyBFTkVSR1kgQlRVIFBFUiBIUg",
              "Name": "PES.AHU.Cooling Energy BTU per Hr"
            },
            {
              "WebId": "P09KoOKByvc0-uxyvoTV1UfQ7FoCAAVVRJTC1QSS1QXFBFUy5BSFUuSEVBVElORyBFTkVSR1kgQlRVIFBFUiBIUg",
              "Name": "PES.AHU.Heating Energy BTU per Hr"
            }
        }

        returns:
        It returns a list with point names and a dictionary with name : Web_ID

        """

        # compose url
        point_search="/points?nameFilter="
        query_string=self.root+"dataservers/"+dataserver+point_search+point_query
        parms={"startIndex":0,"maxCount":100000,"selectedFields": "Items.WebId;Items.Name"}
        
        # call request library
        response=req.get(query_string, parms)

        # parse result and return it
        return self._parse_point(response,include_WebID)
        

    def search_by_path (self, 
                        path_query,
                        include_WebID=True,
                        ):

        """ 
        This method searches for path allowing * operators. It returns path list and a Dictionary with paths:WebIDs
        
        arguments:

        path_query: point name expression (allows *)
        include_WebID: by default True, ut returns list AND a dictionary {name : Web_ID, ...}


        Example API json returned:


        {
          "WebId": "A0EbgZy4oKQ9kiBiZJTW7eugwS5GAMtE55BGIPhgDcyrprwcrOde7rrSVobodgP17EChQVVRJTC1BRlxDRUZTXFVDREFWSVNcQlVJTERJTkdTXFJJRkxFIFJBTkdFXEVMRUNUUklDSVRZfERFTUFORF9LQlRV",
          "Name": "Demand_kBtu"
        }

        NOTE: this is different from the JSON obtained by search_by_point

        returns:
        It returns a list with point names and a dictionary with name : Web_ID

        """

        # compose url
        path_search="attributes?path=\\"   #when searching with a path, need to include this part. Only real difference from search_by_point
        query_string=self.root+path_search+path_query # query_string does not need dataserver. 
        
        #        print query_string # "//' needs extra for escape character or else will not evaluate correctly.
        
        parms={"startIndex":0,"maxCount":100000,"selectedFields": "WebId;Name"} #Json no longer need items, because single item returned. Different from search_by_point
        
        # call request library
        response=req.get(query_string, parms)
        print response #Should be getting a Response of 200 if successful
        # parse result and return it
        return self._parse_path(response,include_WebID)


    def get_webID_by_point (self, 
                               point_name,
                               dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q"  # defaults to buildings dataserver
                              ):

        """
        This method is to make sure we get a single WebID as result of the get_stream_by_point search

        """

        pointList, PointDic=self.search_by_point(point_name, include_WebID=True)
        
        if len (pointList)>1:
            print "warining: the query returned more than one WebID n=%d, \
            only the first one is used\n returning only first" %len (pointList)
        Web_ID_=PointDic[pointList[0]]

#        print Web_ID_
        return Web_ID_


    def get_webID_by_path (self, 
                               path_name,
                              ):

        """
        This method is to make sure we get a single WebID as result of the get_stream_by_path search

        """

        pointList, PointDic=self.search_by_path(path_name, include_WebID=True) #finding webId with path name
        
        if len (pointList)>1:
            print "warning: the query returned more than one WebID n=%d, \
            only the first one is used\n returning only first" %len (pointList)
        Web_ID_=PointDic[pointList[0]]

        print Web_ID_
        return Web_ID_


    def get_stream (self, Web_ID=None, 
                      _start="y", 
                      _end="t", 
                      _calculation="interpolated",
                      _interval="1h",
                      _sumType="All",
                      _label=None):
        """ 
        This method gets the stream given a WebID. It works with one stream at the time.
        
        arguments: 
        Web_ID=None : - the unique identifier of the time series 
        _start="y" : - start date, default yesterday "y"; can use different formats as "YYYY-MM-DD";
        _end="t" : - end date, default yesterday "t"; can use different formats as "YYYY-MM-DD";        
        _calculation="interpolated": can use "recorded" to get raw data and summary to get summary data (tot, mean, sd);
        note: summary data is not a time series, but a dictionary
        _interval="1h": interpolation interval, used only with interpolated; default 1 hour
        _sumType="All" : used if calculation is "summary", can use All, Total, default All
        _label=None : used to pass around name of the column in the dataframe or can overwrite it
     
        returns:
        DataFrame object for TS
        dictionary for summary
        single value for end

        """                
       
        # call function that constructs the http call for method /streams (see PI API manual for API details)
        response=self._compose_stream_url(Web_ID,_start,_end,_calculation,_interval, _sumType, _label)

        # prints for testing: <Response [200]> means it works
        print response

        # parse the response
        if _calculation == (("interpolated") or ("recorded")):            
            result=self._parse_TS(response,Web_ID,_label)
        elif _calculation == ("summary"):
            result=self._parse_summary(response,Web_ID,_label)
        elif _calculation == ("end"):
            result=self._parse_end(response,Web_ID,_label)

        return result

  
    def get_stream_by_point(self,
                                 point_names,
                                _start="y", 
                                _end="t", 
                                _calculation="interpolated",
                                _interval="1h",
                                _sumType="All",
                                _label=None,
                                dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q",  # defaults to UCD buildings dataserver
                                WebID_dic=None
                                ):                                    
        """ 
        This method gets the stream given a the point name. 
        It calls get_webID_by_point to get a single Web ID by point name
        Then it calls the stream using the Web ID
        It also works with multiple points, but it is not optimized (can save time by calling batches)
        
        arguments: 
        point_names : name or list of PI point names
        _start="y" : - start date, default yesterday "y"; can use different formats as "YYYY-MM-DD";
        _end="t" : - end date, default yesterday "t"; can use different formats as "YYYY-MM-DD";        
        _calculation="interpolated": can use "recorded" to get raw data and summary to get summary data (tot, mean, sd);
        note: summary data is not a time series, but a dictionary
        _interval="1h": interpolation interval, used only with interpolated; default 1 hour
        _sumType=All : used if calculation is "summary", can use All, Total, default All
        _label=None : used to pass around name of the column in the dataframe or can overwrite it
 

        returns:
        DataFrame object for TS
        dictionary for summary
        single value for end

        """
        # if send a list of points downloads all of them then merges it into a dataframe
        
        # case 1: multiple streams
        if isinstance(point_names, list):
            
            streams_df=pd.DataFrame()

            for point_name in point_names:

#                print point_name
                Web_ID=self.get_webID_by_point(point_name,dataserver,)
                stream=self.get_stream(Web_ID,_start,_end,_calculation, _interval, _sumType, _label=point_name)
                #stream.name=point_name

                if streams_df.empty:
                    streams_df=pd.DataFrame(stream)
                else:
                    streams_df=streams_df.join(stream, how="outer")

            return streams_df

        # case 2: single stream
        else:

            Web_ID=self.get_webID_by_point(point_names,dataserver)
            stream=self.get_stream(Web_ID,_start,_end,_calculation, _interval, _sumType, _label=point_names)

        return stream


    def get_stream_by_path(self, 
                                 path_names,
                                _start="y", 
                                _end="t", 
                                _calculation="interpolated",
                                _interval="1h",
                                _sumType="All",
                                _label=None,
                                WebID_dic=None
                                ):

        """ 
        This method gets the stream given a the the path.
        Since the path is the key of the database the call to the API does not use the dataserver as before (points names are are unique only on a dataserver) -> the url composed is a bit different 
        It calls get_webID_by_path to get a single Web ID by path
        Then it calls the stream using the Web ID
        It also works with multiple paths, but it is not optimized (can save time by calling batches)
        
        arguments: 
        path_names : name or list of PI paths
        _start="y" : - start date, default yesterday "y"; can use different formats as "YYYY-MM-DD";
        _end="t" : - end date, default yesterday "t"; can use different formats as "YYYY-MM-DD";        
        _calculation="interpolated": can use "recorded" to get raw data and summary to get summary data (tot, mean, sd);
        note: summary data is not a time series, but a dictionary
        _interval="1h": interpolation interval, used only with interpolated; default 1 hour
        _sumType=All : used if calculation is "summary", can use All, Total, default All
        _label=None : used to pass around name of the column in the dataframe or can overwrite it
    
        returns:
        DataFrame object for TS
        dictionary for summary
        single value for end

        """

        # if send a list of points downloads all of them then merges it into a dataframe
        # Same as get_stream_by_point except for variable names and values passed into function calls.

        # case 1: multiple streams
        if isinstance(path_names, list):
            
            streams_df=pd.DataFrame()

            for path_name in path_names:

#                print path_name
                Web_ID=self.get_webID_by_path(path_name) #getting webID with given path name
                stream=self.get_stream(Web_ID,_start,_end,_calculation, _interval, _sumType, _label=path_name)
                #stream.name=path_name

                if streams_df.empty:
                    streams_df=pd.DataFrame(stream)
                else:
                    streams_df=streams_df.join(stream, how="outer")

            return streams_df

        # case 2: single stream
        else:

            Web_ID=self.get_webID_by_path(path_names)
            stream=self.get_stream(Web_ID,_start,_end,_calculation, _interval, _sumType, _label=path_names)

        return stream

    

    