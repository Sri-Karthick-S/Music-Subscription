import boto3
from botocore.exceptions import ClientError

# Define your S3 bucket name (replace with your actual bucket name)
S3_BUCKET = 'artistimages-rmit-assignment'

# Initialize S3 client (adjust region if necessary)
s3_client = boto3.client('s3', region_name='us-east-1')

def get_presigned1_url(s3_key, expiration=3600):
    """
    Generate a pre-signed URL for the S3 object identified by s3_key.
    :param s3_key: The object key in the S3 bucket.
    :param expiration: Time in seconds for the presigned URL to remain valid.
    :return: A pre-signed URL as a string or None if an error occurs.
    """
    try:
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': S3_BUCKET, 'Key': s3_key},
                                               ExpiresIn=expiration)
    except ClientError as e:
        print("S3 error:", e.response['Error']['Message'])
        return None
    return url
