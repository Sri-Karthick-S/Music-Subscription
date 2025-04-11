import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
subscriptions_table = dynamodb.Table('subscriptions')
songs_table = dynamodb.Table('songs')  # New table for song validation

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))

        # Normalize inputs
        email = body.get('email', '').strip().lower()
        song = body.get('song', '').strip().lower()

        if not email or not song:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Email and song are required'})
            }

        # ✅ Check if song exists in 'songs' table
        song_check = songs_table.get_item(Key={'tittle': song})
        if 'Item' not in song_check:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Song not found in the library'})
            }

        # ✅ Check if already subscribed
        response = subscriptions_table.get_item(Key={'email': email, 'song': song})
        if 'Item' in response:
            return {
                'statusCode': 409,
                'body': json.dumps({'message': 'Already subscribed'})
            }

        # ✅ Add subscription
        subscriptions_table.put_item(Item={
            'email': email,
            'song': song
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Subscribed successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': str(e)})
        }
