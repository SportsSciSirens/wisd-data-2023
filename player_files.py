import math
import numpy as np
import pandas as pd
import pickle as pkl
import json
import timeit
from datetime import datetime, date

track_df = pd.read_json(path_or_buf="games/0042100406/0042100406_tracking.jsonl", lines=True)

#Explode column data into individual players for Home and Away Teams and rename columns 
df2_home = pd.json_normalize(track_df['homePlayers'])
df2_away = pd.json_normalize(track_df['awayPlayers'])
df2_home = df2_home.rename(columns={0:'HP1',1:'HP2',2:'HP3',3:'HP4',4:'HP5'})
df2_away = df2_away.rename(columns={0:'AP1',1:'AP2',2:'AP3',3:'AP4',4:'AP5'})
# Add relevant data to the dataframes from the original data
df2_away['frameIdx'] = track_df['frameIdx']
df2_away['period'] = track_df['period']
df2_away['gameClock'] = track_df['gameClock']
df2_away['ball'] = track_df['ball']
# Add relevant data to the dataframes from the original data
df2_home['frameIdx'] = track_df['frameIdx']
df2_home['period'] = track_df['period']
df2_home['gameClock'] = track_df['gameClock']
df2_home['ball'] = track_df['ball']

#UNCOMMENT FOR HOME PLAYERS 
#Seperate XYZ, Player ID, and add relevant information to Players' individual dataframe 
# away_P1_ID = []
# away_P1_X = []
# away_P1_Y = []
# for i in range(len(df2_away)):
#     ID = df2_home['HP5'][i]['playerId']
#     P1_X = df2_home['HP5'][i]['xyz'][0]
#     P1_Y = df2_home['HP5'][i]['xyz'][1]
#     away_P1_Y.append(P1_Y)
#     away_P1_ID.append(ID)
#     away_P1_X.append(P1_X)

#UNCOMMENT FOR AWAY PLAYERS 
#Seperate XYZ, Player ID, and add relevant information to Players' individual dataframe 
# away_P1_ID = []
# away_P1_X = []
# away_P1_Y = []
# for i in range(len(df2_away)):
#     ID = df2_away['AP5'][i]['playerId']
#     P1_X = df2_away['AP5'][i]['xyz'][0]
#     P1_Y = df2_away['AP5'][i]['xyz'][1]
#     away_P1_Y.append(P1_Y)
#     away_P1_ID.append(ID)
#     away_P1_X.append(P1_X)
#Add relative data
away_P1_df = pd.DataFrame({'playerId':away_P1_ID, 'X':away_P1_X, 'Y':away_P1_Y})
away_P1_df['gameClock'] = df2_away['gameClock']
away_P1_df['frameIdx'] = df2_away['frameIdx']
away_P1_df['period'] = df2_away['period']

#Calculate Euclidean distance and store in list (ED: SQRT( (X2-X1)^2 + (Y2-Y1)^2 )
dist_list = []

for i in range((len(away_P1_df)-1)):
    j = i+1
    X = away_P1_df['X']
    Y = away_P1_df['Y']
    dist = math.sqrt((X[j]- X[i])**2 + (Y[j] - Y[i])**2)
    dist_list.append(dist)

dist_list.append(0)   
# Add distance column to Dataframe 
away_P1_df['distance'] = dist_list
# Split array so each array has 100 frames 
aray_split = np.array_split(away_P1_df,966)

#For loop to average each split and create new dataframe 
# Average the distance, Average the X, Average the Y, create a range for the Game Clock and Frame Idx, Keep the last Period and keep the Last PlayerID
average_dist = []
player_id = []
avg_X = []
avg_Y = []
frame_range = []
period = []
gameclock = []
gameClock_diff = []
for i in range(len(aray_split)):
    average_dist1 = np.mean(aray_split[i]['distance'])
    avg_X1 = np.mean(aray_split[i]['X'])
    avg_Y1 = np.mean(aray_split[i]['Y'])
    player_id1 = aray_split[i]['playerId'][-1:].values
    period1 = aray_split[i]['period'][-1:].values
    gamec = np.mean(aray_split[i]['gameClock'])
    game_diff = abs(aray_split[i]['gameClock'][-1:].values - aray_split[i]['gameClock'][::len(aray_split)-1].values).round(decimals=2)
    player_id.append(player_id1)
    avg_X.append(avg_X1)
    avg_Y.append(avg_Y1)
    period.append(period1)
    gameclock.append(gamec)
    gameClock_diff.append(game_diff)
    average_dist.append(average_dist1)
#Add Data onto a new Databased
average_AP1_df = pd.DataFrame()
average_AP1_df['playerId'] = player_id
average_AP1_df['period'] = period
average_AP1_df['avg_X'] = avg_X
average_AP1_df['avg_Y'] = avg_Y
average_AP1_df['avg_Distance(ft)'] = average_dist
average_AP1_df['gameClock(s)'] = gameclock
average_AP1_df['gameClockDiff(s)'] = gameClock_diff

#Calculate Speed and add as seperate DF
speed_list= []
#Calculate Speed 
for i in range(len(average_AP1_df)):
    if average_AP1_df['gameClockDiff(s)'][i] == [0]:
        speed = 0
    else:
        speed = average_AP1_df['avg_Distance(ft)'][i]/ average_AP1_df['gameClockDiff(s)'][i]
        speed_list.append(speed)
speed_df = pd.DataFrame(speed_list)

#Save CSV FILES for player dataframe and speed dataframe
folder_path = 'player_dataframes/'
file_name = '0042100406_AP5.csv'
file_path = folder_path + file_name
average_AP1_df.to_csv(file_path, index=False)
speed_name = '0042100406_AP5_speed.csv'
file_path = folder_path + speed_name
speed_df.to_csv(file_path, index=False)