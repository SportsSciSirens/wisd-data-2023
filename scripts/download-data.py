import boto3
import os

from dotenv import load_dotenv
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
            for obj in game_response['Contents']:
                object_key = obj['Key']
                local_file_path = os.path.join(download_directory, object_key)

                # Check if directory exist before download or it will fail.
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                with tqdm(total=obj['Size'], unit='B', unit_scale=True, unit_divisor=1024, desc=object_key) as progress_bar:
                    s3_client.download_file(bucket_name, object_key, local_file_path,
                                            Callback=lambda bytes_transferred: progress_bar.update(bytes_transferred))

except Exception as e:
    print(f"An error occurred: {str(e)}")


