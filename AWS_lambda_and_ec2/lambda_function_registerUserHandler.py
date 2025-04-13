# this Lambda function handles the new user Registration - it gets the required details fom the auth.html page and then check if thhe user already exists, if yes it asks to enter new details if not it gets all the required details and update the DynomoDB login table it the new user.

import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("login")

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('email')
        username = body.get('username')
        password = body.get('password')

        print("Incoming event:", event)

        if not (email and username and password):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing fields"})
            }

        response = table.get_item(Key={"email": email})
        if 'Item' in response:
            return {
                "statusCode": 409,
                "body": json.dumps({"error": "Email already exists"})
            }

        table.put_item(Item={
            "email": email,
            "user_name": username,
            "password": password
        })

        return {
            "statusCode": 201,
            "body": json.dumps({"message": "User registered"})
        }

    except ClientError as e:
        
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    