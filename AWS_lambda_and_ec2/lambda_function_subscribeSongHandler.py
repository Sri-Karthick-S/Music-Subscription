# this lambda function handles the subscrition section, if the use wnatt to subscribe to the song, that song is added to the subscription table with the user details.

import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("subscription")

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('email')
        title_album = body.get('title_album')
        title = body.get('title')
        artist = body.get('artist')
        album = body.get('album')
        year = body.get('year')
        s3_key = body.get('s3_key')

        if not all([email, title_album, title, artist, album, year, s3_key]):
            return {"statusCode": 400, "body": json.dumps({"error": "Missing fields"})}

        table.put_item(Item={
            "email": email,
            "title_album": title_album,
            "title": title,
            "artist": artist,
            "album": album,
            "year": year,
            "s3_key": s3_key
        })

        return {"statusCode": 201, "body": json.dumps({"message": "Subscribed"})}

    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
