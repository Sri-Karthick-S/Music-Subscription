import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table('subscriptions')

def lambda_handler(event, context):
    try:
        # Check if email is passed via query string
        params = event.get('queryStringParameters')
        if not params or 'email' not in params or not params['email'].strip():
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Email is required'})
            }

        email = params['email'].strip().lower()

        # Query subscriptions by email
        response = subscriptions_table.query(
            KeyConditionExpression=Key('email').eq(email)
        )

        songs = [item['song'] for item in response.get('Items', [])]

        return {
            'statusCode': 200,
            'body': json.dumps({'subscriptions': songs})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }
