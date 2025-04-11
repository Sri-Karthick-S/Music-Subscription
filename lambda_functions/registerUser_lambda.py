import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))

        email = body.get('email')
        user_name = body.get('user_name')  
        password = body.get('password')

        if not email or not user_name or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'message': 'Missing required fields'})
            }

        response = table.get_item(Key={'email': email})
        print("get_item response:", response)  # 🧪 Debug line

        if 'Item' in response:
            return {
                'statusCode': 409,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'message': 'Email already exists'})
            }

        table.put_item(Item={
            'email': email,
            'user_name': user_name,  
            'password': password
        })

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'User registered successfully'})
        }

    
    except Exception as e:
        print("Error occurred:", str(e))  # 👈 add this line
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
           },
           'body': json.dumps({'message': str(e)})
        }

        
        
