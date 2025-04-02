import boto3
import json

# Load the JSON file
with open('2025a1.json') as f:
    data = json.load(f)

songs = data['songs']

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('music')

# Iterate and load each song
for song in songs:
    title = song['title']
    artist = song['artist']
    year = song['year']
    album = song['album']
    image_url = song['img_url']

    item = {
        'title': title,
        'album': album,  # Sort key
        'artist': artist,
        'year': year,
        'image_url': image_url
    }

    table.put_item(Item=item)
    print(f"Inserted: {title} ({album})")
