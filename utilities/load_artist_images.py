import boto3
import json
import logging
import requests
from botocore.exceptions import ClientError

# Logging setup
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

class S3ImageUploader:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', region_name='us-east-1')  # Change region if necessary

    def upload_image(self, image_data, key):
        try:
            # Upload the image data as a file-like object
            self.s3_client.put_object(Bucket=self.bucket_name, Key=key, Body=image_data)
            logger.info(f"✅ Uploaded image to {self.bucket_name}/{key}")
        except ClientError as err:
            logger.error("❌ Error uploading image: %s", err)
            raise

class MusicDataLoader:
    def __init__(self, s3_bucket):
        self.s3_uploader = S3ImageUploader(s3_bucket)

    def load_data_from_json(self, json_file):
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
                logger.info("Data loaded from JSON file successfully.")
                return data['songs']
        except Exception as e:
            logger.error("Error loading JSON file: %s", e)
            raise

    def download_and_upload_images(self, song_data):
        for song in song_data:
            img_url = song.get('img_url')
            if not img_url:
                logger.warning("No image URL for song: %s", song.get('title', 'Unknown'))
                continue

            try:
                response = requests.get(img_url)
                response.raise_for_status()  # Raise an error for bad status codes

                # Generate a unique key for the image
                # For example: "artist/song_title.jpg" (you might want to sanitize these values)
                key = f"{song['artist'].replace(' ', '_')}/{song['title'].replace(' ', '_')}.jpg"

                self.s3_uploader.upload_image(response.content, key)
                logger.info(f"📦 Processed image for {song['title']} by {song['artist']}")
            except Exception as e:
                logger.error("Error processing image for %s: %s", song['title'], e)

if __name__ == '__main__':

    bucket_name = 's4040536artistimages'
    json_file = '2025a1.json'

    loader = MusicDataLoader(bucket_name)
    songs = loader.load_data_from_json(json_file)
    loader.download_and_upload_images(songs)
