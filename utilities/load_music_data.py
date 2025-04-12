import boto3
import json
import logging
from botocore.exceptions import ClientError

# Logging setup
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

class MusicDataLoader:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name='us-east-1',
           
        )
        self.table_name = 'music'
        self.table = self.dynamodb.Table(self.table_name)

    def load_data_from_json(self, json_file):
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
                logger.info(" Data loaded from JSON file successfully.")
                return data['songs']  #  Access the nested array
        except Exception as e:
            logger.error("Error loading JSON file: %s", e)
            raise

    def insert_song_data(self, song_data):
        try:
            with self.table.batch_writer() as batch:
                for song in song_data:
                    # Composite sort key using title and album
                    title_album = f"{song['title']}#{song['album']}"  # Composite sort key
                    # Compute the S3 key using artist and title with spaces removed or replaced by underscores
                    s3_key = f"{song['artist'].replace(' ', '_')}/{song['title'].replace(' ', '_')}.jpg"

                    batch.put_item(
                        Item={
                            'artist': song['artist'],            # Partition Key
                            'title_album': title_album,          # Sort Key
                            'title': song['title'],
                            'album': song['album'],
                            'year': song['year'],
                            's3_key': s3_key     # Store the computed S3 key
                        }
                    )
                    logger.info(f" Batched: {song['title']} by {song['artist']}")
        except ClientError as err:
            logger.error(
                "Error: Couldn't batch insert songs. Here's why: %s: %s",
                err.response["Error"]["Code"],
                err.response["Error"]["Message"]
            )
            raise

if __name__ == '__main__':
    loader = MusicDataLoader()
    songs = loader.load_data_from_json('2025a1.json')
    loader.insert_song_data(songs)
