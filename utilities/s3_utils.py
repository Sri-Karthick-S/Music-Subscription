# This module provides utility functions for generating presigned URLs for S3 objects.
# # It includes a function to generate a presigned URL for downloading an image from S3.

import boto3
from botocore.exceptions import ClientError

# Define your S3 bucket name (replace with your actual bucket name)
S3_BUCKET = 'artistimages-rmit-assignment'

# Initialize S3 client (adjust region if necessary)
s3_client = boto3.client('s3', region_name='us-east-1')

def get_presigned1_url(s3_key, expiration=3600):
    
    try:
        url = s3_client.generate_presigned_url('get_object',
                                               Params={'Bucket': S3_BUCKET, 'Key': s3_key},
                                               ExpiresIn=expiration)
    except ClientError as e:
        print("S3 error:", e.response['Error']['Message'])
        return None
    return url
