from PIPy_Datalink import pipy_datalink

def update_tmy():
    downloader = pipy_datalink()
    web_id = "P09KoOKByvc0-uxyvoTV1UfQBNkCAAVVRJTC1QSS1QXE5TUkRCLjEzNjcwOC5PQVQuVE1Z"
    data = downloader.get_stream(Web_ID=web_id,_start="2016-04-01", _end="t")
    data.rename(columns={data.columns[0]: "OAT"}, inplace=True)
    data.dropna()
    data.to_csv("../data/tmy.csv")    

    
def main():
    update_tmy()
    

if __name__ == "__main__":
    main()  