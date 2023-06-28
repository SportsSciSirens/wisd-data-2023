import boto3
from dotenv import load_dotenv
import os
import json
import csv
from tqdm import tqdm

load_dotenv()

try:

    '''
    1. CHECK TO SEE IF ENVIRONMENT VARIABLES ARE SET.
    '''
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    if not bucket_name:
        raise Exception("AWS_BUCKET_NAME environment variable is not set.")
    game_ids = os.getenv('GAME_IDS')
    if not game_ids:
        raise Exception("GAME_IDS environment variable is not set.")
    game_ids = game_ids.split(',')
    download_directory = os.getenv('FILE_PATH_FOR_DATA')
    if not download_directory:
        raise Exception("FILE_PATH_FOR_DATA environment variable is not set.")


    s3_client = boto3.client('s3')

    '''
    02. DOWNLOAD FILES FOR EACH GAME.
    '''
    for game_id in game_ids:

        # Download metadata
        metadata_prefix = f'metadata/{game_id}'
        metadata_response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=metadata_prefix)

        if 'Contents' in metadata_response:
            pass
            for obj in metadata_response['Contents']:
                object_key = obj['Key']
                local_file_path = os.path.join(download_directory, object_key)

                # Check if directory exist before download or it will fail.
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                with tqdm(total=obj['Size'], unit='B', unit_scale=True, unit_divisor=1024, desc=object_key) as progress_bar:
                    s3_client.download_file(bucket_name, object_key, local_file_path,
                                            Callback=lambda bytes_transferred: progress_bar.update(bytes_transferred))

        # Download tracking/events
        game_prefix = f'games/{game_id}'
        game_response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=game_prefix)

        if 'Contents' in game_response:
            pass
            for obj in game_response['Contents']:
                object_key = obj['Key']
                local_file_path = os.path.join(download_directory, object_key)

                # Check if directory exist before download or it will fail.
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                with tqdm(total=obj['Size'], unit='B', unit_scale=True, unit_divisor=1024, desc=object_key) as progress_bar:
                    s3_client.download_file(bucket_name, object_key, local_file_path,
                                            Callback=lambda bytes_transferred: progress_bar.update(bytes_transferred))


    '''
    03. CONVERT JSON TO CSV FOR EACH GAME.
    '''
    # Iterate over the game directories
    for game_dir in tqdm(os.listdir(download_directory + '/games/'), desc='Game Directories'):
        game_dir_path = os.path.join(download_directory, 'games', game_dir)

        # Check if it's a directory
        if os.path.isdir(game_dir_path):
            # Iterate over the files in the game directory
            for file_name in tqdm(os.listdir(game_dir_path), desc='Files', leave=False):
                if file_name.endswith('.jsonl'):
                    jsonl_file_path = os.path.join(game_dir_path, file_name)
                    csv_file_path = os.path.splitext(jsonl_file_path)[0] + '.csv'

                    # Convert JSONL to CSV
                    with open(jsonl_file_path, 'r') as jsonl_file, open(csv_file_path, 'w', newline='') as csv_file:
                        jsonl_lines = jsonl_file.readlines()
                        num_lines = len(jsonl_lines)
                        csv_writer = csv.writer(csv_file)
                        # Write CSV header
                        if num_lines > 0:
                            json_data = json.loads(jsonl_lines[0])
                            csv_writer.writerow(json_data.keys())
                        # Write CSV data rows
                        for line in tqdm(jsonl_lines, desc='Converting', total=num_lines, leave=False):
                            json_data = json.loads(line)
                            csv_writer.writerow(json_data.values())

except Exception as e:
    print(f"An error occurred: {str(e)}")