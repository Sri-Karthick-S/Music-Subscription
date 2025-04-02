import boto3
import json
import requests
from io import BytesIO

# ---------- Config ----------
BUCKET_NAME = 'music-app-artist-images-s3'  
JSON_FILE = '2025a1.json'

# ---------- Setup ----------
s3 = boto3.client('s3')

# ---------- Load JSON ----------
with open(JSON_FILE) as f:
    data = json.load(f)

songs = data['songs']
uploaded = set()

# ---------- Download & Upload ----------
for song in songs:
    img_url = song['img_url']
    artist = song['artist'].replace(" ", "").replace("&", "And")

    if artist in uploaded:
        continue  # Avoid duplicate uploads

    try:
        # Download image from URL
        response = requests.get(img_url)
        response.raise_for_status()

        # Prepare image for S3 upload (in-memory)
        image_data = BytesIO(response.content)
        filename = f"{artist}.jpg"

        # Upload to S3
        s3.upload_fileobj(image_data, BUCKET_NAME, filename)
        print(f"Uploaded {filename} to {BUCKET_NAME}")
        uploaded.add(artist)

    except Exception as e:
        print(f"Failed to upload for {artist}: {e}")
