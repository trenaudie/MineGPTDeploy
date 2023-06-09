from botocore.exceptions import ClientError
import os
import json
import traceback
from datetime import timedelta
import io
import numpy as np
import base64
import zipfile
import openai
import botocore

from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
import boto3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from flask import Flask, request, make_response, jsonify, redirect, session, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session


from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from jwt.exceptions import InvalidTokenError
from flask_mail import Mail, Message

from utils.logger import logger
from utils.ingest import save_file_to_temp, savePdf_1file_to_Pinecone
from utils.redirect_stdout import redirect_stdout_to_logger
from utils.ask_question import ask_question
from utils.printUsers import printUsers
from config import Config
from utils.getchain import createchain_with_filter
from pdf2image import convert_from_bytes
import base64
from error_codes import ERROR_CODES
os.environ['OPENAI_API_KEY'] = Config.openai_api_key
os.environ['PINECONE_API_KEY'] = Config.pinecone_api_key

pinecone.init(
    api_key=os.environ.get('PINECONE_API_KEY'),
    environment="us-east4-gcp",
)
index_name = 'extractive-qa2'
index = pinecone.Index(index_name)
vectorstore = Pinecone.from_existing_index(
    index_name, embedding=OpenAIEmbeddings())

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.PATH_ACCESS_SQL
app.config['SESSION_FILE_DIR'] = 'session_files'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'guiguisecretkey'
app.config['JWT_SECRET_KEY'] = 'guiguisecretkey'
app.secret_key = app.config['SECRET_KEY']
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 * \
    3  # expired sessions are deleted after 3 hr
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # disables jwt caching


# MAIL CONFIG
# ---------------------------------------------------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'MineGPT@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_gmail_password'
app.config['MAIL_DEFAULT_SENDER'] = 'MineGPT@gmail.com'

mail = Mail(app)
# ----------------------------------------------------------------------------


# AWS CONFIG
# ----------------------------------------------------------------------------
aws_session = boto3.Session(aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                            )
bucket_name = 'minesfiles1page'
# ----------------------------------------------------------------------------

# SQL Config
# ----------------------------------------------------------------------------
db = SQLAlchemy(app)
Session(app)
# CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})
CORS(app, resources={
    r"/*": {
        "origins": "*",  # You can specify the allowed origins here
    }
}, supports_credentials=True)
jwt = JWTManager(app)


class DocSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'name': self.filename,
            'file_id': self.file_id,
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    docsources = db.relationship('DocSource', backref='user', lazy=True)
# ----------------------------------------------------------------------------


chat_history = []
confirmation_numbers = {}
# Set up a store for revoked tokens
revoked_token_store = set()

# Add a callback function to check if a token has been revoked
# @jwt.token_in_blacklist_loader
# def check_if_token_is_revoked(decoded_token):
#     jti = decoded_token['jti']
#     return jti in revoked_token_store
# then inside logout
#     jti = get_raw_jwt()['jti']
# revoked_token_store.add(jti)
# unset_jwt_cookies()


@app.route('/')
def index():
    return "hello world"


# Replace with your AWS credentials
aws_access_key_id = Config.AWS_ACCESS_KEY_ID
aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY
aws_region_name = Config.AWS_REGION_NAME  # Replace with the desired AWS region

# Set up the Amazon SES client
ses_client = boto3.client(
    'ses',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region_name
)


def send_email(to, subject, body):
    # Replace with your verified sender email
    sender_email = "21minegpt@gmail.com"
    recipient_email = to
    CHARSET = 'UTF-8'

    try:
        response = ses_client.send_email(
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender_email
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


# Send an email using the Amazon SES client
send_email('recipient@example.com',
           'Subject of the email', 'Body of the email')


@app.route('/ask_confirmation_code', methods=['POST'])
def for_now():
    print("inside ask_confirmation_code")
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify(status='error', message='Invalid data'), 400
    email = str(data.get('email'))
    print(email)
    password = str(data.get('password'))
    print('password', password)
    confirmation_numbers[email] = {
        'confirmation': 666666, 'password': password}
    return jsonify(status='email sent'), 200


# @app.route('/ask_confirmation_code', methods=['POST'])
# def first_step():
#     data = request.get_json()
#     email = data.get('email')
#     if email and email[-22:] == '@etu.minesparis.psl.eu':
#         try:
#             confirmation_number = np.random.randint(100000, 999999)
#             confirmation_numbers[email] = confirmation_number
#             msg = Message("Welcome to Our Service", recipients=[email])
#             body = f"Hello {email},\n\nThank you for registering with our service. Please confirm your email address by entering the following confirmation number in the app:\n\nConfirmation Number: {confirmation_number}\n\nBest regards,\nThe Our Service Team"
#             subject = "[AUTHENTIFICATION]"
#             send_email(subject, body)
#             return jsonify(status='email sent'), 200
#         except:
#             return jsonify(status='failure to send email'), 400
#     else:
#         return jsonify(status='failed registration')


@app.route('/register', methods=['POST'])
def register():
    print("inside register")
    data = request.get_json()
    print(f"data object received : {data}")
    email = str(data.get('email'))
    password = str(data.get('password'))
    # check if the user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        error = ERROR_CODES['ALREADY_REGISTERED']
        return jsonify({'error_code': error['code'], 'error_message': error['message']}), 400
    
    try: 
        #confirmation = int(data.get("confirmation_code"))
        confirmation = 666666
    except ValueError:
        error = ERROR_CODES['INVALID_CONFIRMATION_CODE_TYPE']
        return jsonify({'error_code': error['code'], 'error_message': error['message']}), 401
    password = generate_password_hash(
        password, method='sha256')
    new_user = User(email=email, password=password, docsources=[])
    db.session.add(new_user)
    db.session.commit()
    expires_delta = timedelta(hours=3)
    access_token = create_access_token(
        identity=new_user.id, expires_delta=expires_delta)
    confirmation_numbers.pop(email)
    return jsonify(status='registration successful!', access_token=access_token), 200
    # except:
    #     return jsonify(status='you can only register once')

    #return error if the confirmation code is wrong 
    # else:
    #     error = ERROR_CODES['INVALID_CONFIRMATION_CODE']
    #     return jsonify({'error_code': error['code'], 'error_message': error['message']}), 401


@app.route('/auto-login', methods=['POST'])
@jwt_required()
def auto_login():
    # not really useful
    # authorization_header = request.headers.get('Authorization', None)
    # if authorization_header:
    #     parts = authorization_header.split()
    #     if parts[0].lower() == 'bearer' and len(parts) == 2:
    #         access_token = parts[1]
    try:
        user_id = get_jwt_identity()
        uploaded_documents = DocSource.query.filter_by(user_id=user_id).all()
        filenames = [doc.to_dict() for doc in uploaded_documents]
        return jsonify(status='authenticated', uploaded_docs=filenames), 200
    except InvalidTokenError:
        return jsonify(status='not authenticated'), 201
    except Exception as e:
        raise(f"inside auto-login, error: {e}")
        return jsonify(status='internal server error'), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print("Received data:", data)
    email = data.get('email', None)
    password = data.get('password', None)

    user = User.query.filter_by(email=email).first()
    print("User:", user)  # Add this line

    if user and check_password_hash(user.password, password):
        print("Password check passed")  # Add this line
        # Change this to your desired duration
        expires_delta = timedelta(hours=3)
        access_token = create_access_token(
            identity=user.id, expires_delta=expires_delta)
        # Session handling here
        uploaded_documents = DocSource.query.filter_by(user_id=user.id).all()
        filenames = [doc.to_dict() for doc in uploaded_documents]

        # session id is fixed to user_id, must change later
        return jsonify(status='authenticated', access_token=access_token, uploaded_docs=filenames), 200
    return jsonify(status='incorrect authentification')


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    session.clear()
    return jsonify(status='logged out'), 200


@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    # add real file id
    logger.info("uploading file")
    try:
        uploaded_file = request.files['document']
        file_id = request.form['file_id']

        user_id = get_jwt_identity()  # for testing purposes, with base user id
        if not user_id:
            raise ValueError('Access token is missing or invalid')

        if not uploaded_file:
            raise ValueError('No file was uploaded')

        logger.info(
            f"uploading file {uploaded_file.filename} with id {file_id} for user {user_id} ")

        with redirect_stdout_to_logger(logger):
            # add file to Pinecone
            filepath = save_file_to_temp(uploaded_file)
            filename_only = os.path.basename(filepath)

            # Construct metadata dictionary
            metadata = {'user_id': user_id,
                        'file_id': file_id}

            # Save file to Pinecone with metadata
            meta = savePdf_1file_to_Pinecone(filepath, metadata, vectorstore)
            os.remove(filepath)

            # add file to docsource database
            description = 'File uploaded by user'  # might need to change
            print(
                f'saving docsource with file_id {file_id}, user_id {user_id}, description {description}, filename {filename_only}')
            docsource = DocSource(file_id=file_id, user_id=user_id, description=description,
                                  filename=filename_only)
            db.session.add(docsource)
            db.session.commit()

            return jsonify('File uploaded and saved to the database.', 200)
    except openai.error.AuthenticationError as e:
        error = ERROR_CODES['OPENAI_AUTHENTICATION_ERROR']
        print(f"ERROR code: {error['code']} message: {error['message']}")
        return jsonify({'error_code': error['code'], 'error_message': error['message']}), 401

 
    except ValueError as e:
        if str(e) == 'Access token is missing or invalid':
            return jsonify({'message': 'Access token is missing or invalid'}), 401
        elif str(e) == 'No file was uploaded':
            return jsonify({'message': 'No file was uploaded'}), 400
        else:
            print(f"error type: ", e.__class__, e.__class__)
            return jsonify({'message': 'An unknown error occurred'}), 500


@app.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    print(filename)
    s3 = aws_session.client('s3')
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        user_id = get_jwt_identity()
    if not user_id:
        return 'Session ID is missing or incorrect.', 400

    try:
        # Get the file from S3
        s3_object = s3.get_object(Bucket=bucket_name, Key=filename)
        file_stream = io.BytesIO(s3_object['Body'].read())
        s3 = aws_session.client('s3')
        # Send the file as a response
        return send_file(file_stream, download_name=filename, as_attachment=True)

    except s3.exceptions.NoSuchKey:
        print('File not found')
        return jsonify({'error': 'File not found'}), 404


@app.route('/qa', methods=['POST'])
@jwt_required()
def answerQuestion():
    """Question answering endpoint
    Returns:
    dict with keys "answer", "sources"
    - answer: str
    - sources: list of dicts
        - filename: str
        - text: str
        - page: str (not yet implemented)
        - etc.
    """
    try:
        data = request.get_json()
        question = data.get('prompt')
        chat_history = data.get('chathistory')
        print("chatHistory", chat_history)
        if not chat_history:
            chat_history = []

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            user_id = get_jwt_identity()
            print(auth_header)

        logger.info(
            f"question: {question} for user with user_id {user_id} ")
        with redirect_stdout_to_logger(logger):
            result = ask_question(question, vectorstore, chat_history, user_id) 
            # {'answer' : 'blabla','sources': [{'filename': 'MathS1/CalDiff.pdf', 'text': 'Mathematics 5...', 'page_number': 28.0}, ...]
            print("qa answer is", result['answer'])
            print(result)
        # ex source 1 --> {filename: 'MathS1/CalDiff.pdf', page: 1, text: 'blabla'}
        sources = result["sources"]
        s3 = aws_session.client('s3')

        # if 'am sorry' or 'désolé' or 'cannot find' or 'ne figure pas' or 'ne trouve pas' or 'sorry'in result['answer'][:10]:
        #     print("sorry the documents are not relevant")
        #     error = ERROR_CODES['IRRELEVANT_DOCUMENTS']
        #     return jsonify({'error_code': error['code'], 'error_message': error['message']}), 404

        for i, source in enumerate(sources):
            filename = source['filename']  # ex. Math_S1_Corr1.pdf
            filename, file_extension = os.path.splitext(filename)
            page_number = source['page_number']
            # switch to AWS encoding
            subjectname, lesson_name = filename.split("/", 1)
            if 'temp' in subjectname:
                source['file_img'] = None
                continue
            elif i >= 2 and 'temp' not in subjectname:
                # only put the source name and not the text nor the img
                source['file_img'] = None
            else:  # get the pdf from aws
                try:
                    pageObj_key = f"{subjectname}/{lesson_name}_page{int(page_number):03d}{file_extension}"
                    print("pageObj_key", pageObj_key)
                    s3_object = s3.get_object(
                        Bucket=bucket_name, Key=pageObj_key)
                    file_stream = io.BytesIO(s3_object['Body'].read())
                    file_img = convert_from_bytes(
                        file_stream.getvalue(), dpi=300, fmt='jpeg', single_file=True)[0]
                    image_stream = io.BytesIO()
                    file_img.save(image_stream, format='JPEG')
                    image_stream.seek(0)
                    image_base64 = base64.b64encode(
                        image_stream.getvalue()).decode('utf-8')
                    source['file_img'] = image_base64
                except Exception as e:
                    print(e)
                    source['file_img'] = None

        return jsonify(result), 200
    except openai.error.AuthenticationError as e:
        error = ERROR_CODES['OPENAI_AUTHENTICATION_ERROR']
        print(f"ERROR code: {error['code']} message: {error['message']}")
        return jsonify({'error_code': error['code'], 'error_message': error['message']}), 401
 
    except Exception as e:
        # Log the full traceback of the exception
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/pdf/<path:pdf_key>', methods=['GET'])
def get_pdf(pdf_key):
    try:
        data = request.get_json()
        question = data.get('prompt')
        chat_history = data.get('chathistory')

        chat_history = []

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            user_id = get_jwt_identity()

        with redirect_stdout_to_logger(logger):
            # (question: str, vectorstore: Pinecone,  chat_history: list[dict], user_id: str = None)

            # result = ask_question(question, vectorstore, chat_history, user_id)
            result = {'answer': 'Energy is the capacity to do work or transfer heat, and it exists in various forms, such as potential, kinetic, thermal, electrical, chemical, and nuclear. It can be neither created nor destroyed, according to the law of conservation of energy, but can be transformed from one form to another. Renewable energy sources, like solar, wind, hydro, and geothermal, are becoming more prominent',
                      'sources': [{'filename': 'MathS1/CalDiff.pdf', 'page_number': 1, 'text': "On sait qu'une fonction f definie sur un intervalle ouvert I inclus dans R à valeurs dans R est dérivable"},
                                  {'filename': 'MathS1/CalDiff.pdf', 'page_number': 2, 'text': 'Inversement, on vérifie immédiatement que si une fonction f admet une développement limité du type..'}]}

        # ex source 1 --> {filename: 'MathS1/CalDiff.pdf', page: 1, text: 'blabla'}
        sources = result["sources"]
        s3 = aws_session.client('s3')
        s3_object = s3.get_object(Bucket=bucket_name, Key=pdf_key)
        file_stream = io.BytesIO(s3_object['Body'].read())

        for i, source in enumerate(sources):
            filename = source['filename']  # ex. Math_S1_Corr1.pdf
            filename, file_extension = os.path.splitext(filename)
            page_number = source['page_number']
            # switch to AWS encoding
            subjectname, lesson_name = filename.split("/", 1)
            if 'temp' in subjectname:
                source['file_img'] = None
                continue
            elif i >= 2 and 'temp' not in subjectname:
                # only put the source name and not the text nor the img
                source['text'] = ""
                source['file_img'] = None
            else:  # get the pdf from aws
                pageObj_key = f"{subjectname}/{lesson_name}_page{int(page_number):03d}{file_extension}"
                print("pageObj_key", pageObj_key)

                s3_object = s3.get_object(Bucket=bucket_name, Key=pageObj_key)
                file_stream = io.BytesIO(s3_object['Body'].read())
                file_img = convert_from_bytes(
                    file_stream.getvalue(), dpi=300, fmt='jpeg', single_file=True)[0]
                image_stream = io.BytesIO()
                file_img.save(image_stream, format='JPEG')
                image_stream.seek(0)
                image_base64 = base64.b64encode(
                    image_stream.getvalue()).decode('utf-8')
                source['file_img'] = image_base64

        return jsonify(result), 200

        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/delete', methods=['POST'])
@jwt_required()
def delete_vector():
    user_id = get_jwt_identity()
    data = request.get_json()
    print(
        f"received request to delete vector from user {user_id} with data {data}")
    vectorcount = vectorstore._index.describe_index_stats()[
        'total_vector_count']
    file_id = data.get('file_id', None)
    vectorstore._index.delete(filter={'file_id': file_id, 'user_id': user_id})
    docsource = DocSource.query.filter_by(
        user_id=user_id, file_id=file_id).first()

    if docsource is None:
        return jsonify({'message': 'vector not found'}), 404

    db.session.delete(docsource)
    db.session.commit()

    vectorcount2 = vectorstore._index.describe_index_stats()[
        'total_vector_count']
    if vectorcount2 == vectorcount:
        return jsonify({'message': 'vector not deleted'}), 500
    else:
        print(
            f"deleted vector from user {user_id} with data {data}, removed {vectorcount-vectorcount2} vectors")
        return jsonify({'message': 'vector deleted'}), 200


with app.app_context():
    db.create_all()
#     # print(f"app.py cwd {os.getcwd()}")
#     app_module_dir = os.path.dirname(os.path.abspath(__file__))
#     # print(f"app.py module directory: {app_module_dir}")
#     # print("app.py resolved database path:", db.engine.url.database)
#     # print("inside app py, os.get_cwd()", os.getcwd())

if __name__ == '__main__':
    with app.app_context():
        print("app.py SQLALCHEMY_DATABASE_URI:",
              app.config['SQLALCHEMY_DATABASE_URI'])
        print("all users : ", User.query.all())

    app.run(debug=True, port=5000)


# does changing user name
