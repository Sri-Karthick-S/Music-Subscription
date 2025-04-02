import boto3

# Your RMIT ID base
rmit_id = 's4038609'
first_name = 'Sri Karthick'
last_name = 'Selvam'

# Initialize DynamoDB table
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

# Insert 10 users
for i in range(10):
    email = f"{rmit_id}{i}@student.rmit.edu.au"
    user_name = f"{first_name}{last_name}{i}"
    password = f"{i}{(i+1)%10}{(i+2)%10}{(i+3)%10}{(i+4)%10}{(i+5)%10}"

    item = {
        'email': email,
        'user_name': user_name,
        'password': password
    }

    table.put_item(Item=item)
    print(f"Added: {email} | {user_name} | {password}")
