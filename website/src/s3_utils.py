import boto3
from botocore.exceptions import ClientError
from flask import current_app
import uuid
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path("/home/ec2-user/junseo-yang-portfolio/.env") 
load_dotenv(dotenv_path=env_path)

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION')
    )

def upload_file_to_s3(file, filename=None):
    if filename is None:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    
    try:
        bucket = current_app.config['AWS_S3_BUCKET']
        region = current_app.config['AWS_S3_REGION']
        s3_client = get_s3_client()
        s3_client.upload_fileobj(
            file,
            bucket,
            filename,
            ExtraArgs={'ACL': 'public-read'}
        )
        return f"http://{bucket}.s3.{region}.amazonaws.com/{filename}"
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None
