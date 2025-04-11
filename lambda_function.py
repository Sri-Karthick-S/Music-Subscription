import json
import re
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# table reference
login_table = dynamodb.Table("login")
subscription_table = dynamodb.Table("subscription")

def lambda_handler(event, context):
    try:
        # With proxy integration, the body is a JSON string.
        body = json.loads(event.get("body", "{}"))
    except Exception as e:
        print("Error parsing JSON:", e)
        return _response(400, {"message": "Invalid JSON in request body"})
    print("Decoded body:", body)

    # Check if the required key 'action' exists in the request body.
    if 'action' not in body:
        return _response(400, {"message": "Missing 'action'"})
    # Retrieve the action value to determine which operation to perform
    action = body['action']

    if action == "register":
        # Validate that all required fields are provided.
        required_fields = ["email", "username", "password"]
        for field in required_fields:
            if not body.get(field):
                return _response(400, {"message": f"Missing field: {field}"})

        email = body["email"]
        username = body["username"]
        password = body["password"]

        # Validate the email format using a regular expression.
        # Pattern: starts with 's', followed by exactly 7 digits, then "@student.rmit.edu.au".
        if not re.match(r"^s\d{7}@student\.rmit\.edu\.au$", email):
            return _response(400, {"message": "Invalid email format. Email should be in the format s#######@student.rmit.edu.au"})

        try:
            response = login_table.get_item(Key={'email': email})
            if 'Item' in response:
                # User exists, so return conflict (HTTP 409) with a custom message.
                return _response(409, {"message": "User already exists, please try login."})

            # Insert new user record into DynamoDB.
            login_table.put_item(Item={
                'email': email,
                'user_name': username,
                'password': password
            })
            return _response(200, {"message": "Registration successful"})
        except ClientError as e:
            print("Registration error:", e)
            return _response(500, {"message": "Registration error"})

    elif action == "subscribe":
        # Subscription branch: add a new subscription record
        try:
            email = body.get("email")
            subscription_data = {
                'email': email,
                'title_album': body.get("title_album"),
                'title': body.get("title"),
                'artist': body.get("artist"),
                'album': body.get("album"),
                'year': int(body.get("year", "0")),
                's3_key': body.get("s3_key")
            }
            subscription_table.put_item(Item=subscription_data)
            return _response(200, {"message": "Subscribed"})
        except Exception as e:
            print("Subscribe error:", e)
            return _response(500, {"message": f"Subscription failed: {str(e)}"})

    elif action == "remove_subscription":
        # Removal branch: remove an existing subscription
        try:
            email = body.get("email")
            title_album = body.get("title_album")
            subscription_table.delete_item(Key={'email': email, 'title_album': title_album})
            return _response(200, {"message": "Subscription removed"})
        except Exception as e:
            print("Remove subscription error:", e)
            return _response(500, {"message": f"Failed to remove subscription: {str(e)}"})

    else:
        return _response(400, {"message": f"Unknown action: {action}"})

# Helper function to create a consistent response format for API Gateway.
def _response(status_code, body_obj):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS"
        },
        "body": json.dumps(body_obj)
    }
