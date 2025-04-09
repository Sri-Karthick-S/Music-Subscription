import boto3

dynamodb = boto3.resource('dynamodb')

table = dynamodb.create_table(
    TableName='subscription',
    KeySchema=[
        {'AttributeName': 'email', 'KeyType': 'HASH'},        # Partition Key
        {'AttributeName': 'title_album', 'KeyType': 'RANGE'}  # Sort Key
    ],
    AttributeDefinitions=[
        {'AttributeName': 'email', 'AttributeType': 'S'},
        {'AttributeName': 'title_album', 'AttributeType': 'S'}
    ],
    BillingMode='PAY_PER_REQUEST'
)

# Wait until created
table.meta.client.get_waiter('table_exists').wait(TableName='subscription')
print("Subscription table created.")
