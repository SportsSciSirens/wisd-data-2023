import os
import json
import glob

import uuid
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from tqdm import tqdm


'''
SETUP ENVIRONMENT VARIABLES
'''
load_dotenv()

try:
    data_directory = os.getenv('FILE_PATH_FOR_DATA')
    if not data_directory:
        raise Exception("FILE_PATH_FOR_DATA environment variable is not set.")

except Exception as e:
    print(f"An error occurred: {str(e)}")
    exit(1)

# PostgreSQL table names
tracking_table_name = 'tracking'
event_table_name = 'events'

# Function to create the database
def create_database(db_name):
    # Connect to the PostgreSQL server without specifying a database
    conn = psycopg2.connect(host='localhost', port='5432', user='postgres')

    # Disable autocommit mode
    conn.autocommit = True

    # Create a new cursor for creating the database
    cursor = conn.cursor()

    # Execute the CREATE DATABASE statement outside of a transaction
    cursor.execute(f'CREATE DATABASE {db_name};')

    # Close the cursor and the connection
    cursor.close()
    conn.close()

# Function to create tables if they don't exist
def create_tables(db_name):
    # Connect to the PostgreSQL server
    connection = psycopg2.connect(host='localhost', port='5432', user='postgres', dbname=db_name)

    with connection.cursor() as cursor:
        # Create the tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking (
                frameIdx SERIAL,
                finalsId int,
                homePlayers JSONB,
                awayPlayers JSONB,
                ball JSONB,
                period INTEGER,
                gameClock FLOAT,
                gameClockStopped BOOLEAN,
                shotClock FLOAT,
                wallClock BIGINT
            )
        ''')

        # Create the events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                eventId UUID,
                finalsId int,
                gameId UUID,
                eventType VARCHAR(255),
                shotClock FLOAT,
                gameClock FLOAT,
                wallClock BIGINT,
                period INTEGER,
                homePlayers JSONB,
                awayPlayers JSONB,
                playerId UUID,
                pbpId UUID
            )
        ''')

        # Commit the changes to the database
        connection.commit()

    # Close the connection
    connection.close()

def drop_tables(db_name):
    # Connect to the PostgreSQL server with the specified database
    connection = psycopg2.connect(host='localhost', port='5432', user='postgres', dbname=db_name)

    with connection.cursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS event, tracking')

    # Commit the changes
    connection.commit()

    # Close the connection
    connection.close()


def ingest_tracking_data(db_name):
    # Connect to the PostgreSQL server with the specified database
    connection = psycopg2.connect(host='localhost', port='5432', user='postgres', dbname=db_name)

    tracking_files = glob.glob(os.path.join(data_directory, 'games', '*', '*_tracking.jsonl'))

    for tracking_file in tracking_files:
        with open(tracking_file) as tracking_data_file:
            tracking_data = tracking_data_file.readlines()

            with connection.cursor() as cursor:
                total_entries = len(tracking_data)
                print(f'Ingesting tracking data from {tracking_file}...')

                # Extract the finalsId from the tracking file path
                finals = tracking_file.split('/')[-2]

                # Ingest tracking data
                for tracking_line in tqdm(tracking_data, desc=f'Progress - {tracking_file}', unit='entry'):
                    tracking_item = json.loads(tracking_line)
                    tracking_item['homePlayers'] = json.dumps(tracking_item['homePlayers'])
                    tracking_item['awayPlayers'] = json.dumps(tracking_item['awayPlayers'])

                    tracking_values = [finals] + [json.dumps(tracking_item.get(column)) for column in tracking_item.keys()]

                    tracking_insert_query = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                        sql.Identifier(tracking_table_name),
                        sql.SQL(', ').join([sql.Identifier('finalsId')] + list(map(lambda col: sql.Identifier(col.lower()), tracking_item.keys()))),
                        sql.SQL(', ').join([sql.Placeholder()] * (len(tracking_item.keys()) + 1))  # Include an additional placeholder for finalsId
                    )
                    cursor.execute(tracking_insert_query, tracking_values)

                # Commit the changes
                connection.commit()

    # Close the connection
    connection.close()


def ingest_event_data(db_name):
    # Connect to the PostgreSQL server with the specified database
    connection = psycopg2.connect(host='localhost', port='5432', user='postgres', dbname=db_name)

    event_files = glob.glob(os.path.join(data_directory, 'games', '*', '*_events.jsonl'))

    for event_file in event_files:
        with open(event_file) as event_data_file:
            event_data = event_data_file.readlines()

            with connection.cursor() as cursor:
                total_entries = len(event_data)
                print(f'Ingesting event data from {event_file}...')

                # Ingest event data
                for event_line in tqdm(event_data, desc=f'Progress - {event_file}', unit='entry'):
                    event_item = json.loads(event_line)
                    event_item['eventId'] = str(uuid.uuid4())

                    event_values = [
                        str(event_item['eventId']),
                        str(event_item.get('gameId')) if event_item.get('gameId') else None,
                        event_item.get('eventType'),
                        float(event_item.get('shotClock')) if event_item.get('shotClock') else None,
                        float(event_item.get('gameClock')) if event_item.get('gameClock') else None,
                        int(event_item.get('wallClock')) if event_item.get('wallClock') else None,
                        int(event_item.get('period')) if event_item.get('period') else None,
                        json.dumps(event_item.get('homePlayers')) if event_item.get('homePlayers') else None,
                        json.dumps(event_item.get('awayPlayers')) if event_item.get('awayPlayers') else None,
                        str(event_item.get('playerId')) if event_item.get('playerId') else None,
                        event_item.get('pbpId')
                    ]

                    event_insert_query = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                        sql.Identifier(event_table_name),
                        sql.SQL(', ').join(map(lambda col: sql.Identifier(col.lower()), event_item.keys())),
                        sql.SQL(', ').join(sql.Placeholder() * len(event_item.keys()))
                    )
                    cursor.execute(event_insert_query, event_values)

                # Commit the changes
                connection.commit()

    # Close the connection
    connection.close()


# Call the necessary functions
wd_db = 'wisd_2023'
# create_database(wd_db)
create_tables(wd_db)
ingest_tracking_data(wd_db)
# ingest_event_data(wd_db)

drop_tables(wd_db)
