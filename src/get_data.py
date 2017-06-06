"""
This file tests getting Data from the PI_datalink stream
"""

import os
import time 

import pandas as pd

from pi_datalink import PIDatalink

def cache_point(point_name, start="2014", end="t", remove_duplicates=True):
    """
    Gets the stream and saves the data in CSV format

    Parameters:
    point_name: name of data point
    start: start parameter
    end: end parameter
    remove_duplicates: flag
    """
    path = "".join(["../data/", point_name, ".csv"])
    
    # Imports previous CSV if it exists    
    if os.path.isfile(path):
        stream = pd.read_csv(path, index_col=0, parse_dates=True)
    else:
        stream = pd.DataFrame()
        
    downloader = PIDatalink()
    stream2 = downloader.get_stream_by_point(point_name, start, end)
    
    # Remove NA entries that might be from the future and save space
    stream2.dropna(inplace=True) 
    
    # Join with previous CSV and is sorted
    if stream.empty:
        stream = stream2
    else:
        stream = stream.append(stream2)
        
        if remove_duplicates:
            stream = stream[~stream.index.duplicated()]
            stream.sort_index(inplace=True)
    
    stream.to_csv(path)
    return stream

def get_point(point_names, start="2014", end="t"):
    """
    Gets the data point from the data stream

    Parameters:
    point_names: Names of data points
    start: start parameter
    end: end parameter
    """
    streams = pd.DataFrame()

    if not isinstance(point_names, list):
        point_names = [point_names]
        
    for point_name in point_names:
        stream = pd.DataFrame()
        path = "".join(["../data/", point_name, ".csv"])
        
        # Fetch point_name if found in cache
        if os.path.isfile(path):
            stream = pd.read_csv(path, index_col=0, parse_dates=True)
            
            # Rewrite "t" as date to search in csv
            if end == "t":
                end = time.strftime("%m/%d/%Y 00:00:00")

            # Download if range is found in stream
            if end not in stream.index:
                last_update = stream.index[-1]
                stream2 = cache_point(point_name, last_update, end, remove_duplicates=False)
                stream2.drop(last_update, inplace=True)
                stream = stream.append(stream2)

        # Download from PI database if not found 
        else:
            stream = cache_point(point_name)
      
        if streams.empty:
            streams = stream
        else:
            streams = streams.join(stream, how="outer")
         
    return streams
        
def main():
    """
    Main function. Initializes sample data point to cache
    """
    cache_point("NSRDB.136708.OAT.TMY")

if __name__ == "__main__":
    main()  
