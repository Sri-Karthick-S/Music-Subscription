import json
import boto3

def lambda_handler(event, context):
    email = event['queryStringParameters'].get('email')
    password = event['queryStringParameters'].get('password')
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')

    response = table.get_item(Key={'email': email})
    
    if 'Item' in response and response['Item']['password'] == password:
        return {
            'statusCode': 200,
            'body': json.dumps({'user_name': response['Item']['user_name']})
        }
    else:
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Invalid email or password'})
        }
