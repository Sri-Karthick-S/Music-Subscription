import json
import boto3

dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table('subscriptions')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))

        email = body.get('email', '').strip().lower()
        song = body.get('song', '').strip()

        if not email or not song:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Email and song are required'})
            }

        # Check if subscription exists
        response = subscriptions_table.get_item(Key={'email': email, 'song': song})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Subscription not found'})
            }

        # Delete the subscription
        subscriptions_table.delete_item(Key={'email': email, 'song': song})

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Unsubscribed successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }

