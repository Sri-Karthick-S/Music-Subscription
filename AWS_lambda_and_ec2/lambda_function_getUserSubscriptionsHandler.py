# this is the lambda function which handles subscription of the user loged in, and also displays the corresponding images of the song they have subscribed.


import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("subscription")

s3 = boto3.client("s3")
BUCKET_NAME = "artistimages-rmit-assignment"

def generate_presigned_url(s3_key):
    try:
        return s3.generate_presigned_url('get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600)
    except Exception as e:
        print("Error generating URL:", e)
        return ""

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('email')

        if not email:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing email"})}

        response = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email))
        items = response.get('Items', [])

        for item in items:
            s3_key = item.get('s3_key')
            item['image_url'] = generate_presigned_url(s3_key) if s3_key else ""

        return {
            "statusCode": 200,
            "body": json.dumps(items)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }