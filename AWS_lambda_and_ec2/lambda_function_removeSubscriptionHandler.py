# this lambda function is handles the rmoval of the song subscription from the DynomoDB subscription tablle

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

        if not email or not title_album:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing fields"})}

        table.delete_item(Key={
            "email": email,
            "title_album": title_album
        })

        return {"statusCode": 200, "body": json.dumps({"message": "Unsubscribed"})}

    except ClientError as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
