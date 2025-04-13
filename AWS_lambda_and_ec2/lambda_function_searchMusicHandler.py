# this lambda function handles the Query section, with the entered details from the fields it search the DynoomoDB music table and retrieves the list of the values that matches the query. and also it displays the corresponding image of the song it retrieved.

import json
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
table = dynamodb.Table("music")
BUCKET = "artistimages-rmit-assignment"

def generate_presigned_url(key):
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=3600
        )
    except Exception as e:
        print("Presigned URL error:", e)
        return ""

def lambda_handler(event, context):
    try:
        criteria = json.loads(event['body'])

        title_query = criteria.get('title', '').lower()
        artist_query = criteria.get('artist', '').lower()
        album_query = criteria.get('album', '').lower()
        year_query = criteria.get('year', '').lower()

        response = table.scan()
        items = response.get('Items', [])

        def matches(item):
            return (
                (not title_query or title_query in item.get('title', '').lower()) and
                (not artist_query or artist_query in item.get('artist', '').lower()) and
                (not album_query or album_query in item.get('album', '').lower()) and
                (not year_query or year_query in str(item.get('year', '')).lower())
            )

        filtered = list(filter(matches, items))

        #  Add presigned image URL
        for item in filtered:
            s3_key = item.get("s3_key", "")
            item["image_url"] = generate_presigned_url(s3_key)

        return {
            "statusCode": 200,
            "body": json.dumps(filtered)
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as ex:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(ex)})
        }