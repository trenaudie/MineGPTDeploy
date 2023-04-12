import boto3
from botocore.exceptions import ClientError
import os
from logger import logger
import sys
sys.path.append('/Users/tanguyrenaudie/Documents/TanguyML/MineGPT/backend')
from config import Config


# Create a new session using the access key and secret access key of the new user
session = boto3.Session(aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                        region_name=Config.AWS_REGION_NAME)
bucket_name = 'minefiles'

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        #print working directory
        print(os.getcwd())
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True


if __name__ == "__main__":

    # Create an IAM client
    iam = session.client('iam')

    # Call the get_user() method to get information about the current user
    response = iam.get_user()

    # Print the user's username
    print('Current user:', response['User'])



    upload_file('backend/temp/Probabilite1.pdf', bucket_name)