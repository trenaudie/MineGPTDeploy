

import boto3
import os

import PyPDF2
import sys
from io import BytesIO
sys.path.append(os.getcwd())

from backend.utils.redirect_stdout import redirect_stdout_to_logger
from backend.config import Config
from botocore.exceptions import ClientError
from backend.utils.logger import logger

# Create a new session using the access key and secret access key of the new user
session = boto3.Session(aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
bucket_name = 'minefiles'


def printUserStats(session:boto3.Session):
    # Create an IAM client
    iam = session.client('iam')

    # Call the get_user() method to get information about the current user
    user = iam.get_user()

    # Print the user's username
    print('Current user:', user['User'])
    print('current region ', session.region_name)

    # Get the policies attached to the user
    attached_policies = iam.list_attached_user_policies(
        UserName=user['User']['UserName'])

    # Get the inline policies attached to the user
    inline_policies = iam.list_user_policies(
        UserName=user['User']['UserName'])

    all_policies = iam
    # Print the policy ARNs
    for policy in attached_policies['AttachedPolicies']:
        print(policy['PolicyArn'])

    for policy in inline_policies['PolicyNames']:
        policy_document = iam.get_user_policy(
            UserName=user['User']['UserName'], PolicyName=policy)
        print(policy_document['PolicyArn'])
    # upload_file('backend/temp/Probabilite1.pdf', bucket_name)

        # Get the groups the user belongs to
    groups = iam.list_groups_for_user(UserName=user['User']['UserName'])

    # Print the group names
    for group in groups['Groups']:
        print(group['GroupName'])

    response = iam.list_attached_group_policies(
        GroupName='mineGPTgroup',
    )
    print("group policies ", response)

    
def delete_file_from_s3(file_key, bucket_name, session):
    # Create an S3 client
    s3_client = session.client('s3')
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        print(f"Deleted file {file_key} from bucket {bucket_name}")
    except ClientError as e:
        print(f"Error deleting file {file_key} from bucket {bucket_name}: {e}")
        return False
    return True

def delete_folder_from_s3(folder_key, session):
    bucket_name = 'minefiles'
    s3_client = session.client('s3')
    for obj in s3_client.list_objects(Bucket=bucket_name, Prefix=folder_key)['Contents']:
        if len(obj['Key'].split('/')) == 2: 
            print("deleting ", obj['Key'])
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
            except ClientError as e:
                print(f"Error deleting file {obj['Key']} from bucket {bucket_name}: {e}")
                return False
        

def get_subject(filename_only:str) -> str:
    """parse out the subject from the filename_only 
    ex. MMC_PC1.pdf -> MMC
    """
    if '_' in filename_only:
        return filename_only.split("_")[0]
    elif '.' in filename_only:
        return filename_only.split(".")[0]
    else:
        return ''


def upload_file(filepath, session: boto3.Session):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    filename, fileextension = os.path.splitext(filepath)
    filename_only = os.path.basename(filename)
    subject_name = get_subject(filename_only)

    s3_client = session.client('s3')
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for pagenbr in range(len(reader.pages)):
            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[pagenbr])
            aws_object_name = f"{subject_name}/{filename_only}_page{pagenbr:03d}{fileextension}"
            with BytesIO() as bytes_stream:
                writer.write(bytes_stream)
                bytes_stream.seek(0)
                session = boto3.Session(aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY)
                print("writing to s3 with object_name", aws_object_name)
                try : 
                    s3_client.upload_fileobj(bytes_stream, "minefiles", aws_object_name)
                except ClientError as e:
                    logger.error(e)
                    return False
                
def upload_Admin(folder, bucket_name, session):
    for root, dirs, files in os.walk(folder):
        for filename in files:
            item_path = os.path.join(root, filename)
            if os.path.isfile(item_path):
                # Get the relative path from the root folder
                rel_path = os.path.relpath(item_path, folder)
                # Replace path separators with underscores
                new_filename = rel_path.replace(os.path.sep, '_')
                print(filename)
                # Upload the file
                upload_file(item_path, new_filename, bucket_name, session)


def split_pdf(filepath: str) -> None:
    """Splits a PDF file into one-page PDF files, that it stores to temp"""
    filename, fileextension = os.path.splitext(filepath)
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for pagenbr in range(len(reader.pages)):
            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[pagenbr])
            output_filename = f"{filename}_page{pagenbr:03d}{fileextension}"
            with open(output_filename, 'wb') as out:
                writer.write(out)
            print(f'Created: {output_filename}')




if __name__ == "__main__":
    #assuming this is running from /minegptDeploy

    # upload_file('backend/testarticles/ECUE61.1corrige-exo-4.pdf', session)
    print(os.getcwd())
    delete_folder_from_s3('MMC', session)

    pass