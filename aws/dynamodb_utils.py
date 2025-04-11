import boto3

dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('login')

def check_login(email, password):
    email = email.strip().lower()
    password = password.strip()

    try:
        response = login_table.get_item(Key={'email': email})
        item = response.get('Item')
        print("DEBUG: Fetched item ->", item)  # 🔍 ADD THIS LINE
        if item and item['password'] == password:
            return item
        else:
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def register_user(email, username, password):
    email = email.strip().lower()
    response = login_table.get_item(Key={'email': email})
    if 'Item' in response:
        return "exists"
    
    login_table.put_item(Item={
        'email': email,
        'user_name': username,
        'password': password
    })
    return "success"

