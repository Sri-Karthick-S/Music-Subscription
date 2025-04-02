import boto3

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb')

# Create table
table_name = 'music'

try:
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {'AttributeName': 'title', 'KeyType': 'HASH'},  # Partition key
            {'AttributeName': 'album', 'KeyType': 'RANGE'}  # Sort key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'title', 'AttributeType': 'S'},
            {'AttributeName': 'album', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'  # On-demand pricing
    )

    # Wait until table is created
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f"Table '{table_name}' created successfully!")

except Exception as e:
    print(f"Error creating table: {e}")
