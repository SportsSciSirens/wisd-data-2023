```text

  ___ ___ ___ _______ ______       ______         __             _______ _______ _______ _______ 
 |   Y   |   |   _   |   _  \     |   _  \ .---.-|  |_.---.-.   |       |   _   |       |   _   |
 |.  |   |.  |   1___|.  |   \    |.  |   \|  _  |   _|  _  |   |___|   |.  |   |___|   |___|   |
 |. / \  |.  |____   |.  |    \   |.  |    |___._|____|___._|    /  ___/|.  |   |/  ___/ _(__   |
 |:      |:  |:  1   |:  1    /   |:  1    /                    |:  1  \|:  1   |:  1  \|:  1   |
 |::.|:. |::.|::.. . |::.. . /    |::.. . /                     |::.. . |::.. . |::.. . |::.. . |
 `--- ---`---`-------`------'     `------'                      `-------`-------`-------`-------'
                                                                                                 
```


## Table of Contents
* [Overview](#)
* [Prerequisites](#)
* [Download Data](#download-data)

## Overview
This is our getting started codebase where you will be provided a script and steps to download the file.
```text
+-------------------------------+       +-------------------------------+
|            events             |       |           tracking            |
+-------------------------------+       +-------------------------------+
| eventId (UUID, PK)            |<------|       gameId (UUID, PK, FK)    |
| gameId (UUID)                 |       |       frameIdx (SERIAL, PK)    |
| eventType (VARCHAR(255))      |       |       homePlayers (JSONB)      |
| shotClock (FLOAT)             |       |       awayPlayers (JSONB)      |
| gameClock (FLOAT)             |       |       ball (JSONB)             |
| wallClock (BIGINT)            |       |       period (INTEGER)         |
| period (INTEGER)              |       |       gameClock (FLOAT)        |
| homePlayers (JSONB)           |       |       gameClockStopped (BOOLEAN)|
| awayPlayers (JSONB)           |       |       shotClock (FLOAT)        |
| playerId (UUID)               |       |       wallClock (BIGINT)       |
| pbpId (UUID)                  |       +-------------------------------+
+-------------------------------+

```
## Prerequisites
* Python v3.10
* AWS Credentials

## Download Data
Verify that you have installed Python version 3.8 or later and have a copy of the SportsRadar AWS Credentials.

### Setup Virtual Environment
1. Run `python -m venv venv` to establish virtual environment.
2. Run `source venv/bin/activate` to activate python virtual environment.
3. Run `pip install -r requirements.txt` to download script dependencies

### Running the script
1. Create a `.env` file at the root of the codebase
2. Copy the contents of `.env.template` into the newly created `.env` file.
3. Update the following values based on the instructions provided in the **#general** channel of the slack.
```text
AWS_BUCKET_NAME
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```
> 📝: FILE_PATH_FOR_DATA set it to whatever file path you wish to store the data.

4. Run `python download-data.py` and the script will proceed to download all the data from the SportsRadar S3 bucket. 

### Store Data in PostgreSQL
- `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`