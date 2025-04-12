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
    
    print("inside check login")
    print(email, password)
    try:
        response = login_table.get_item(Key={'email': email})
        print("after get item")
    except ClientError as e:
        print("DynamoDB error:", e.response['Error']['Message'])
        print("error")
        return None
    else:
        # print(response,response['Item']['password'] )
        if 'Item' in response and response['Item']['password'] == password:
            print("success")
            print(response['Item'])
            return response['Item']
    return None

def register_user(email, username, password):
    
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


# ----- Subscription Functions -----

def get_user_subscriptions(email):
    
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
    
def email_exists(email):
    try:
        response = login_table.get_item(Key={'email': email})
        return 'Item' in response
    except ClientError:
        return False