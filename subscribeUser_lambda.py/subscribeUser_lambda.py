import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('subscriptions')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))

        email = body.get('email')
        song = body.get('song')

        if not email or not song:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Missing email or song'})
            }

        # Check if already subscribed
        response = table.get_item(Key={'email': email, 'song': song})
        if 'Item' in response:
            return {
                'statusCode': 409,
                'body': json.dumps({'message': 'Already subscribed'})
            }

        # Add to subscriptions
        table.put_item(Item={'email': email, 'song': song})

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Subscribed successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }
