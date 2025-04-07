import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

# Initialize DynamoDB resource once (adjust region if necessary)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Reference the login table
login_table = dynamodb.Table('login')
# Reference the music table
music_table = dynamodb.Table('music')
# Reference the subscriptions table
subscription_table = dynamodb.Table('subscription')

def check_login(email, password):
    """Check user credentials from the login table."""
    try:
        response = login_table.get_item(Key={'email': email})
    except ClientError as e:
        print("DynamoDB error:", e.response['Error']['Message'])
        return None
    else:
        if 'Item' in response and response['Item']['password'] == password:
            return response['Item']
    return None

def register_user(email, username, password):
    """Register a new user if the email does not exist."""
    try:
        response = login_table.get_item(Key={'email': email})
    except ClientError as e:
        print("DynamoDB error:", e.response['Error']['Message'])
        return "error"
    if 'Item' in response:
        return "exists"
    try:
        login_table.put_item(Item={
            'email': email,
            'user_name': username,
            'password': password
        })
    except ClientError as e:
        print("DynamoDB error:", e.response['Error']['Message'])
        return "error"
    return "success"

def search_music(criteria):
    """
    Search the music table based on the provided criteria.
    criteria is a dictionary with possible keys: 'title', 'artist', 'album', 'year'
    """
    # Build filter expression
    filter_expression = None
    for key, value in criteria.items():
        if value:
            condition = Attr(key).contains(value)
            filter_expression = condition if filter_expression is None else filter_expression & condition

    try:
        if filter_expression:
            response = music_table.scan(FilterExpression=filter_expression)
        else:
            response = music_table.scan()
        return response.get('Items', [])
    except ClientError as e:
        print("Search error:", e.response['Error']['Message'])
        return []
'''
def search_music(criteria):
    """
    Search the music table based on the provided criteria.
    criteria is a dictionary with possible keys: 'title', 'artist', 'album', 'year'
    """
    filter_expression = None
    for key, value in criteria.items():
        if value:
            if key == 'year':
                try:
                    # Convert the year value from string to int
                    num_value = int(value)
                except ValueError:
                    continue  # Skip invalid year values
                condition = Attr(key).eq(num_value)
            else:
                condition = Attr(key).contains(value)
            filter_expression = condition if filter_expression is None else filter_expression & condition

    try:
        if filter_expression:
            response = music_table.scan(FilterExpression=filter_expression)
        else:
            response = music_table.scan()
        return response.get('Items', [])
    except ClientError as e:
        print("Search error:", e.response['Error']['Message'])
        return []
    '''
# ----- Subscription Functions -----

def get_user_subscriptions(email):
    """
    Retrieve all subscription records for the given user from the subscriptions table.
    Each record should contain at least:
       - user_email (partition key)
       - song_id (sort key) : unique identifier for the song, e.g. "title_album"
       - title, artist, album, year, s3_key (for displaying details and S3 image)
    """
    try:
        response = subscription_table.query(
            KeyConditionExpression=Key('email').eq(email),
            ConsistentRead=True
        )
        return response.get('Items', [])
    except ClientError as e:
        print("Error retrieving subscriptions:", e.response['Error']['Message'])
        return []

def subscribe_song(email, song_data):
    """
    Subscribe the user to a song.
    song_data should be a dict containing:
       - song_id: unique song identifier (e.g. composite key "title_album")
       - title, artist, album, year, s3_key (for the image)
    """
    try:
        subscription_table.put_item(Item={
            'email': email,
            'title_album': song_data['title_album'],
            'title': song_data['title'],
            'artist': song_data['artist'],
            'album': song_data['album'],
            'year': song_data['year'],
            's3_key': song_data['s3_key']
        })
        return True
    except ClientError as e:
        print("Error subscribing song:", e.response['Error']['Message'])
        return False

def remove_subscription(email, title_album):
    """Remove a subscription record for the user."""
    try:
        subscription_table.delete_item(
            Key={
                'email': email,
                'title_album': title_album
            }
        )
        return True
    except ClientError as e:
        print("Error removing subscription:", e.response['Error']['Message'])
        return False