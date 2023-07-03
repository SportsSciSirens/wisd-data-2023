import os
import pandas as pd
from dotenv import load_dotenv
from py_ball import playbyplay

load_dotenv()

try:
    data_directory = os.getenv('FILE_PATH_FOR_DATA')
    if not data_directory:
        raise Exception("FILE_PATH_FOR_DATA environment variable is not set.")
    list_of_ids = os.getenv('GAME_IDS')
    if not list_of_ids:
        raise Exception("GAME_IDS environment variable is not set.")
    list_of_ids = list_of_ids.split(',')
except Exception as e:
    print(f"An error occurred: {str(e)}")

# create empty EVENT dataframe list
eventDataframes = []

 # append datasets into the EVENT dataframes
for i in range(len(list_of_ids)):
    file_path_for_events = f'{data_directory}/games/{list_of_ids[i]}/{list_of_ids[i]}_events.csv'
    # tempEvent_df = pd.read_csv(f"games/"+list_of_ids[i]+"/"+list_of_ids[i]+"_events.csv")
    tempEvent_df = pd.read_csv(file_path_for_events)
    eventDataframes.append(tempEvent_df)



#create empty TRACKING dataframe list
trackingDataframes = []

# append datasets into the TRACKING dataframes
for i in range(len(list_of_ids)):
    file_path_for_tracking = f'{data_directory}/games/{list_of_ids[i]}/{list_of_ids[i]}_tracking.csv'
    # tempTracking_df = pd.read_csv("games/"+list_of_ids[i]+"/"+list_of_ids[i]+"_tracking.csv")
    tempTracking_df = pd.read_csv(file_path_for_tracking)
    trackingDataframes.append(tempTracking_df)




#### Pull PBP ####
# Header information to pass along to the stats.nba.com API to make it play nicely
# taken from Women-in-Sports-Data repo
# Go to your developer tools in your browser to access the HEADERS. In the filter box, seacrh for 'Request Headers' and copy your 'User-Agent' key

HEADERS = {'Connection': 'keep-alive',
            'Host': 'stats.nba.com',
            'Origin': 'http://stats.nba.com',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'stats.nba.com',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Accept-Language': 'en-US,en;q=0.9',
            "X-NewRelic-ID": "VQECWF5UChAHUlNTBwgBVw==",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +\
                            ' AppleWebKit/537.36 (KHTML, like Gecko)' + \
                            ' Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'} # will have to change this specific line to match your User-Agent




"""
Mapping WISD events data to py_ball pbp

Creates a list of 18 dataframes (each game {wisd event file} mapped to pbp)

"""
  
### Creating list of pbp games ###
pbpDataframes = []

for game_id in list_of_ids:
    plays = playbyplay.PlayByPlay(headers=HEADERS,
                                endpoint='playbyplayv2',
                                game_id=game_id)
    play_df =pd.DataFrame(plays.data['PlayByPlay'])
    pbpDataframes.append(play_df)


### Creating list of mapped pbp data and wisd events ###
jointEventPbp = []
i = 0

while i < len(eventDataframes):
    for event_df in eventDataframes :
        play_df = pbpDataframes[i]
        joint_df = event_df.merge(play_df, left_on="pbpId", right_on="EVENTNUM", how="left")
        jointEventPbp.append(joint_df)
        i+=1



# Checking mapping
ecf_1 = jointEventPbp[0]
print(ecf_1[ecf_1["pbpId"]==7][["eventType", "shotClock", "gameClock", "VISITORDESCRIPTION", "PCTIMESTRING"]])
