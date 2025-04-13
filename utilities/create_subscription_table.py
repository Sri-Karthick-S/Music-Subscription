# This script creates a DynamoDB table named 'subscription' with the following attributes:

# create_subscription_table.py
import boto3
import logging
from botocore.exceptions import ClientError

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def create_subscription_table():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table_name = 'subscription'

    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    if table_name in existing_tables:
        logger.info(f" Table '{table_name}' already exists.")
        return
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'email', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'title_album', 'KeyType': 'RANGE'}  # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'email', 'AttributeType': 'S'},
                {'AttributeName': 'title_album', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.wait_until_exists()
        logger.info(f" Created subscription table: {table_name}")
    except ClientError as err:
        logger.error(f" Failed to create table: {err.response['Error']['Message']}")
        raise

if __name__ == '__main__':
    create_subscription_table()
    logger.info("Subscription table creation script executed.")
