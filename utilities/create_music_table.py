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
        )
        self.table = None
        self.newly_created = False  # <-- flag to track table creation

    def create_table(self):
        try:
            # Check if table already exists
            existing_tables = self.dynamodb.meta.client.list_tables()['TableNames']
            if self.table_name in existing_tables:
                self.table = self.dynamodb.Table(self.table_name)
                logger.info("ℹ️ Table '%s' already exists. Skipping creation.", self.table_name)
                self.newly_created = False
                return self.table

            # Create new table
            self.table = self.dynamodb.create_table(
                TableName=self.table_name,
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
            self.newly_created = True

        except ClientError as err:
            logger.error(
                "❌ Error: Couldn't create table %s. %s: %s",
                self.table_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"]
            )
            raise

        return self.table

if __name__ == '__main__':
    manager = MusicTable()
    manager.create_table()

    if manager.newly_created:
        # Optionally insert music records here
        logger.info("🚀 Ready to populate the 'music' table with songs.")