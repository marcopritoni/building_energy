import os

import pandas as pd

from PIPy_Datalink import pipy_datalink

# tag name NSRDB.136708.OAT.TMY
def cache_tmy(start="2014", end="t"):
    downloader = pipy_datalink()
    web_id = "P09KoOKByvc0-uxyvoTV1UfQBNkCAAVVRJTC1QSS1QXE5TUkRCLjEzNjcwOC5PQVQuVE1Z"
    data = downloader.get_stream(web_id, start, end)
    data.rename(columns={data.columns[0]: "OAT"}, inplace=True)
    data.to_csv("../data/tmy.csv")
    return data

def cache_point(data_name, start="2014", end="t"):
    downloader = pipy_datalink()
    data = downloader.get_stream_by_point(data_name, start, end) 
    data.to_csv("".join(["../data/", data_name, ".csv"]))
    return data

def get_point(point_names, start="2014", end="t"):
    streams = pd.DataFrame()

    if not isinstance(point_names, list):
        point_names = [point_names]
        
    for point_name in point_names:
        stream = pd.DataFrame()
        path = "".join(["../data/", point_name, ".csv"])
        
        #TODO: Check if cache in time range!
        # Fetch point_name if found in cache
        if os.path.isfile(path):
            stream = pd.read_csv(path, index_col=0, parse_dates=True)
            
        # Else download from PI database
        else:
            stream = cache_point(point_name)
        
        
        if streams.empty:
            streams = stream
        else:
            streams = streams.join(stream, how="outer")
            

                
    return streams
        
def main():
    cache_tmy()
    cache_point("OAT")

if __name__ == "__main__":
    main()  