import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
music_table = dynamodb.Table('music')
login_table = dynamodb.Table('login')
subscription_table = dynamodb.Table('subscription')

def check_login(email, password):
    response = login_table.get_item(Key={'email': email})
    if 'Item' in response and response['Item']['password'] == password:
        return response['Item']
    return None

def register_user(email, username, password):
    response = login_table.get_item(Key={'email': email})
    if 'Item' in response:
        return "exists"
    login_table.put_item(Item={
        'email': email,
        'user_name': username,
        'password': password
    })
    return "success"

def get_subscriptions(email):
    response = subscription_table.query(
        KeyConditionExpression=Key('email').eq(email)
    )
    return response.get('Items', [])

def add_subscription(email, song_data):
    title_album = f"{song_data['title']}_{song_data['album']}"

    # Check if already subscribed
    response = subscription_table.get_item(
        Key={'email': email, 'title_album': title_album}
    )
    if 'Item' in response:
        return "already_subscribed"

    subscription_table.put_item(Item={
        'email': email,
        'title_album': title_album,
        **song_data
    })
    return "success"

def remove_subscription(email, title, album):
    title_album = f"{title}_{album}"
    subscription_table.delete_item(
        Key={'email': email, 'title_album': title_album}
    )
    return "removed"

def search_music(filters):
    expr = None
    for key, val in filters.items():
        if val:
            if expr is None:
                expr = Attr(key).contains(val)
            else:
                expr = expr & Attr(key).contains(val)

    if not expr:
        return []

    response = music_table.scan(FilterExpression=expr)
    return response.get('Items', [])