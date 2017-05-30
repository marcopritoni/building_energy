
'''
This class is a wrapper for PI web API

It replicates the functions of PI datalink excel Add-on (Windows only) in Python

Some features may be UC Davis specific, but can easily be extended to other PI installations

@author Marco Pritoni <marco.pritoni@gmail.com>
latest update: Feb 14 2017 

TODO:
-return a df from summary
--from API
-pass dic from search to make retrieve data quicker for multi-points
-use batch API calls for several datapoints at the same time
-add path search

'''

# Standard library imports
import json
import logging

# Third-party library imports
import numpy as np
import pandas as pd
import requests as req

class pipy_datalink(object):

    def __init__(self, root=None, calculation=None, interval=None, buildingMeterDB=None):

        if root == None:

            # for more general application this root should be read from config
            # file in not set as an arg
            self.root = "https://ucd-pi-iis.ou.ad3.ucdavis.edu/piwebapi/"

    def search_by_point(self,
                        point_query,
                        dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q",
                        include_WebID=True,
                        ):
        """ 
        This method searches for points allowing * operators. It returns point list and a Dictionary with names:WebIDs

        arguments:

        point_query: name expression
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
        point_search = "/points?nameFilter="
        query_string = self.root + "dataservers/" + \
            dataserver + point_search + point_query
        parms = {"startIndex": 0, "maxCount": 100000,
                 "selectedFields": "Items.WebId;Items.Name"}

        # call request library
        response = req.get(query_string, parms)

        # parse result and return it
        return self._parse_point(response, include_WebID)

    def get_webID_by_point(self,
                           point_name,
                           # defaults to buildings dataserver
                           dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q"
                           ):
        """
        This method is to make sure we get a single WebID as result of the get_stream_by_point search

        """

        pointList, PointDic = self.search_by_point(
            point_name, include_WebID=True)

        if len(pointList) > 1:
            logging.warning('Query returned more than one WebID n=%d, \
            only the first one is used\n returning only first' % len(pointList))
        Web_ID_ = PointDic[pointList[0]]

        logging.info(Web_ID_)
        return Web_ID_

    def get_stream_by_point(self,
                            point_names,
                            _start="y",
                            _end="t",
                            _calculation="interpolated",
                            _interval="1h",
                            _sumType=None,
                            _label=None,
                            # defaults to UCD buildings dataserver
                            dataserver="s09KoOKByvc0-uxyvoTV1UfQVVRJTC1QSS1Q",
                            WebID_dic=None
                            ):
        """ 
        This method gets the stream given a the point name. 
        It calls get_webID_by_point to get the Web ID by point name
        Then it calls the stream using the Web ID
        It also works with multiple points 

        arguments: 
        point_names : name or list of PI point names
        _start="y" : - start date, default yesterday "y"; can use different formats as "YYYY-MM-DD";
        _end="t" : - end date, default yesterday "t"; can use different formats as "YYYY-MM-DD";        
        _calculation="interpolated": can use "recorded" to get raw data and summary to get summary data (tot, mean, sd);
        note: summary data is not a time series, but a dictionary
        _interval="1h": interpolation interval, used only with interpolated; default 1 hour
        _sumType=None : used if calculation is "summary", can use All, Total, default Total
        _label=None : not used at the moment; needed for future extensions

        returns:
        DataFrame object for TS
        dictionary for summary
        single value for end

        """
        # if send a list of points downloads all of them then merges it into a
        # dataframe

        # case 1: multiple streams
        if isinstance(point_names, list):

            streams_df = pd.DataFrame()

            for point_name in point_names:

                logging.info(point_name)
                Web_ID = self.get_webID_by_point(point_name, dataserver,)
                stream = self.get_stream(
                    Web_ID, _start, _end, _calculation, _interval, _sumType, _label=point_name)
                # stream.name=point_name

                if streams_df.empty:
                    streams_df = pd.DataFrame(stream)
                else:
                    streams_df = streams_df.join(stream, how="outer")

            return streams_df

        # case 2: single stream
        else:

            Web_ID = self.get_webID_by_point(point_names, dataserver)
            stream = self.get_stream(
                Web_ID, _start, _end, _calculation, _interval, _sumType, _label=point_names)

        return stream

    def get_stream(self, Web_ID=None,
                   _start="y",
                   _end="t",
                   _calculation="interpolated",
                   _interval="1h",
                   _sumType=None,
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
        _sumType=None : used if calculation is "summary", can use All, Total, default Total
        _label=None : not used at the moment; needed for future extensions

        returns:
        DataFrame object for TS
        dictionary for summary
        single value for end

        """

        # call function that constructs the http call for method /streams (see
        # PI API manual for API details)
        response = self._compose_stream_url(
            Web_ID, _start, _end, _calculation, _interval, _sumType, _label)

        # prints for testing: <Response [200]> means it works
        logging.info(response)

        # parse the response
        if _calculation == (("interpolated") or ("recorded")):
            result = self._parse_TS(response, Web_ID, _label)
        elif _calculation == ("summary"):
            result = self._parse_summary(response, Web_ID, _label)
        elif _calculation == ("end"):
            result = self._parse_end(response, Web_ID, _label)

        return result

    def _compose_stream_url(self, Web_ID,
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
        Web_ID_string = self.root + "streams/" + Web_ID + "/" + _calculation
        logging.info(Web_ID_string)

        # constructs the parameters for requests REST api call
        if _sumType:
            parms = {"startTime": _start, "endTime": _end,
                     "interval": _interval, "summaryType": _sumType}
        else:
            parms = {"startTime": _start,
                     "endTime": _end, "interval": _interval}

        # call python library for json/http REST API
        response = req.get(Web_ID_string, parms)
        return response

    def _parse_point(self, response, include_WebID):
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

        js = json.loads(response.text)

        # save results in a list of points and a dict of {point_name: Web_ID}
        point_list = []
        point_dic = {}

        # PARSE what is returned
        # for each element in the json structure
        for elem in range(0, len(js["Items"])):

            Point_name_full = js["Items"][elem]["Name"]  # see example
            point_list.append(Point_name_full)

            # can also return dict
            if include_WebID:
                Web_ID_ = js["Items"][elem]["WebId"]
                point_dic[Point_name_full] = Web_ID_

        try:
            return point_list, point_dic
        except:
            return point_list, point_dic

    def _parse_TS(self, response, Web_ID, _label):
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
            js = json.loads(response.text)

            timeseries = {}
            # counts the elements
            n_elem = len(js["Items"])

            # loops through the json in search of timestep and value - note
            # this is not vectorized as the structure is irregular
            for i in range(0, n_elem):

                # saves timestep
                timestamp = js["Items"][i]["Timestamp"]

                # saves value - unless the calculated value is missing (failed
                # calculation)
                value = js["Items"][i]["Value"]
                try:
                    # format to float
                    float(value)
                    pass
                except:
                    # if calculation failed can ignore the results (nan)
                    value = np.nan
                    # or can get the default value: fixed
                    # value=js["Items"][i]["Value"]["Value"]

                # saves timeseries and value in a dictionary
                timeseries[timestamp] = value

            # converts dict into pandas series
            ts = pd.Series(timeseries)

            # converts Series index to datetime type
            ts.index = pd.to_datetime(ts.index)

            # saves name of the Series
            if _label:

                # uses lable provided
                ts.name = _label

            else:

                # uses the WebID if label not provided
                ts.name = Web_ID
            ts = pd.DataFrame(ts)

        # If the requests fails
        else:
            # print to screen error
            logging.error("I can't find the stream with this WebID")

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
            js = json.loads(response.text)

            # counts the elements
            n_elem = len(js["Items"])
            summary_dic = {}
            # print js["Items"] # print to test
            # loops through the json to extract each summary value
            for i in range(0, n_elem):
                sumType = js["Items"][i]['Type']
                SumVal = js["Items"][i]['Value']['Value']
                summary_dic[sumType] = SumVal

            df_summ = pd.DataFrame.from_dict(summary_dic, orient='index')

            if _label:
                df_summ.columns = [_label]

            else:
                df_summ.columns = [Web_ID]

            return df_summ

        else:
            # print error to screen
            logging.error("I can't find the stream with this WebID")
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
            js = json.loads(response.text)

            end_dic = {}

            # save json object in a dictionary
            end_dic['Good'] = js['Good']
            end_dic['Timestamp'] = js['Timestamp']
            end_dic['Value'] = js['Value']

            df_end = pd.DataFrame.from_dict(end_dic, orient='index')

            if _label:
                df_end.columns = [_label]

            else:
                df_end.columns = [Web_ID]

            return df_end

        else:
            # print to screen error
            logging.error("Cannot find stream with this WebID")

        return js['Value']
