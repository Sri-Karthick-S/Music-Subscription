# this Lambda function handles the login credentials and check if it existes in the DynamoDB login table. checks if the user has entered valid credentisls.

import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("login")

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('email')
        password = body.get('password')

        if not (email and password):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing email or password"})
            }

        # Check if user exists
        response = table.get_item(Key={'email': email})
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "User not found"})
            }

        user = response['Item']
        if user['password'] != password:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Incorrect password"})
            }

        # Success – return user info (excluding password ideally)
        return {
            "statusCode": 200,
            "body": json.dumps({
                "email": user['email'],
                "user_name": user.get('user_name', '')
            })
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
