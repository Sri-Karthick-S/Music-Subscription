import boto3

dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('login')

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
