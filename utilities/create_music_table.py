import boto3
import logging
from botocore.exceptions import ClientError

# Logging setup
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

class MusicTable:
    def __init__(self):
        self.table_name = 'music'
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name='us-east-1',
            #endpoint_url='http://localhost:8000'  # DynamoDB Local
        )
        self.table = None

    def create_table(self):
        try:
            self.table = self.dynamodb.create_table(
                TableName='music',
                KeySchema=[
                    {'AttributeName': 'artist', 'KeyType': 'HASH'},
                    {'AttributeName': 'title_album', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'artist', 'AttributeType': 'S'},
                    {'AttributeName': 'title_album', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )

            self.table.wait_until_exists()
            logger.info("✅ Table '%s' created successfully.", self.table_name)
        except ClientError as err:
            logger.error(
                "Error: Couldn't create table %s. Here's why: %s: %s",
                self.table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"]
            )
            raise
        else:
            return self.table

if __name__ == '__main__':
    manager = MusicTable()
    manager.create_table()
