import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

# Initialize DynamoDB resource once (adjust region if necessary)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Reference the login table
login_table = dynamodb.Table('login')
# Reference the music table
music_table = dynamodb.Table('music')

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
'''
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