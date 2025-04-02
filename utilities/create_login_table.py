import boto3
import logging
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

class LoginTable:
    def __init__(self, student_id, first_name, last_name):
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name='us-east-1',
            #endpoint_url='http://localhost:8000'  # For DynamoDB Local
        )
        self.table_name = 'login'
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.table = None

    def create_table(self):
        try:
            self.table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'email', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'email', 'AttributeType': 'S'}
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
                err.response["Error"]["Message"],
            )
            raise
        else:
            return self.table

    def populate_users(self):
        if not self.table:
            self.table = self.dynamodb.Table(self.table_name)

        for i in range(10):
            email = f"{self.student_id}{i}@student.rmit.edu.au"
            username = f"{self.first_name}{self.last_name}{i}"
            password = f"{i}{(i+1)%10}{(i+2)%10}{(i+3)%10}{(i+4)%10}{(i+5)%10}"  # Generates 6-digit pattern

            try:
                self.table.put_item(
                    Item={
                        'email': email,
                        'user_name': username,
                        'password': password
                    }
                )
                logger.info(f"👤 Inserted user: {email}")
            except ClientError as err:
                logger.error(
                    "Error: Couldn't insert user %s. Error: %s",
                    email,
                    err.response["Error"]["Message"]
                )

if __name__ == '__main__':
    # Replace with your real values
    manager = LoginTable(
        student_id="s312345",
        first_name="Thara",
        last_name="Sonu"
    )
    manager.create_table()
    manager.populate_users()
