import boto3
import requests

dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('login')

def check_login(email, password):
    url = "https://m0uoz68yl6.execute-api.us-east-1.amazonaws.com/dev"  
    params = {"email": email, "password": password}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.RequestException as e:
        print(f"Error calling login API: {e}")
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
