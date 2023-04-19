from botocore.exceptions import ClientError
import os
import json
import traceback
from datetime import timedelta
import io
import numpy as np
import base64
import zipfile

from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
import boto3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from flask import Flask, request, render_template, jsonify, redirect, session, url_for, send_file
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
bucket_name = 'minefiles'
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'name': self.filename,
            'source': '',
            'folderId': None,
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    docsources = db.relationship('DocSource', backref='user', lazy=True)
# ----------------------------------------------------------------------------


chat_history = []
chain = createchain_with_filter(vectorstore)
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
    data = request.get_json()
    email = str(data.get('email'))
    confirmation = int(data.get("confirmation_code"))
    print(confirmation)
    print(email)
    print('confirmation value', confirmation_numbers[email]['confirmation'])
    print(confirmation_numbers[email]['password'])
    # try:
    if confirmation == confirmation_numbers[email]['confirmation']:
        password = generate_password_hash(
            confirmation_numbers[email]['password'], method='sha256')
        new_user = User(email=email, password=password, docsources=[])
        db.session.add(new_user)
        db.session.commit()
        # Change this to your desired duration
        expires_delta = timedelta(hours=3)

        access_token = create_access_token(
            identity=new_user.id, expires_delta=expires_delta)
        confirmation_numbers.pop(email)
        return jsonify(status='registration successful!', access_token=access_token), 200
        # except:
        #     return jsonify(status='you can only register once')
    else:
        print("failed registration")
        return jsonify(status='failed registration')


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
            print('successfully saved file to temp', filepath)
            filename_only = os.path.basename(filepath)

            # Construct metadata dictionary
            metadata = {'user_id': user_id,
                        'file_id': file_id}

            # Save file to Pinecone with metadata
            meta = savePdf_1file_to_Pinecone(filepath, metadata, vectorstore)
            print('successfully saved file to Pinecone', meta)
            os.remove(filepath)

            # add file to docsource database
            description = 'File uploaded by user'  # might need to change

            docsource = DocSource(user_id=user_id, description=description,
                                  filename=filename_only)
            db.session.add(docsource)
            db.session.commit()

            return jsonify('File uploaded and saved to the database.', 200)

    except ValueError as e:
        if str(e) == 'Access token is missing or invalid':
            return jsonify({'message': 'Access token is missing or invalid'}), 401
        elif str(e) == 'No file was uploaded':
            return jsonify({'message': 'No file was uploaded'}), 400
        else:
            raise(str(e))
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
        # with redirect_stdout_to_logger(logger):
        #     # (question: str, vectorstore: Pinecone,  chat_history: list[dict], user_id: str = None)

        #     result = ask_question(question, vectorstore, chat_history, user_id)
        #     print("qa result is", result)

        sources = [{'filename': 'Math_S1_TopoCD4quizz.pdf', 'page': '3', 'text': 'bla bla bla'},
                   {'filename': 'Math_S1_TopoCD4quizz.pdf', 'page': '3', 'text': 'bla bla bla'}]

        result = {'answer': "I don't know", 'sources': sources}
        s3 = aws_session.client('s3')

        pdf_files = []
        for source in sources:
            filename = source['filename']
            folder, doc = os.path.split(filename)
            if 'temp' not in folder:
                s3_object = s3.get_object(Bucket=bucket_name, Key=filename)
                file_stream = io.BytesIO(s3_object['Body'].read())
                pdf_base64 = base64.b64encode(
                    file_stream.getvalue()).decode('utf-8')
                pdf_files.append(pdf_base64)

        # Your JSON result data
        result['pdf_files'] = pdf_files
        pdf_data = base64.b64decode(pdf_base64)

        with open('decoded_pdf.pdf', 'wb') as file:
            file.write(pdf_data)

        # Combine the `processed_text
        # ` and `page_content` JSON objects into a single dictionary
        return jsonify(result)

    except Exception as e:
        # Log the full traceback of the exception
        print(traceback.format_exc())
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
    vectorstore._index.delete(
        filter={'file_id': data['file_id'], 'user_id': user_id})
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
