import os
import json
import traceback
from datetime import timedelta


from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from flask import Flask, request, render_template, jsonify, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session


from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


from utils.logger import logger
from utils.ingest import save_file_to_Pinecone, save_file_to_temp, save_file_to_Pinecone_metadata
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SESSION_FILE_DIR'] = 'session_files'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'guiguisecretkey'
app.config['JWT_SECRET_KEY'] = 'guiguisecretkey' 
app.secret_key = app.config['SECRET_KEY']
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 * \
    3  # expired sessions are deleted after 3 hr

db = SQLAlchemy(app)
Session(app)
# CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})
CORS(app, resources={
    r"/*": {
        "origins": "*",  # You can specify the allowed origins here
    }
}, supports_credentials= True)
jwt = JWTManager(app)


class DocSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'filename': self.filename,
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    docsources = db.relationship('DocSource', backref='user', lazy=True)


chat_history = []
chain = createchain_with_filter(vectorstore)


@app.route('/')
def index():
    return "hello world"


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    if email and email[-22:] == '@etu.minesparis.psl.eu':
        try:
            password = generate_password_hash(
                data.get('password'), method='sha256')
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            expires_delta = timedelta(hours=3)  # Change this to your desired duration
            access_token = create_access_token(identity=new_user.id, expires_delta=expires_delta)
            return jsonify(status='registration successful!', access_token=access_token), 200
        except:
            return jsonify(status='you can only register once'), 400
    else:
        return jsonify('failed registration. You must have a @etu.minesparis.psl.eu address'), 400


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
   
    if user and check_password_hash(user.password, password):
        expires_delta = timedelta(hours=3)  # Change this to your desired duration
        access_token = create_access_token(identity=user.id,expires_delta=expires_delta)
        # Session handling here

        return jsonify(status='authenticated', access_token=access_token), 200 #session id is fixed to user_id, must change later 
    return jsonify(status='incorrect authentification'), 400


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    session.clear()
    return jsonify(status='logged out'), 200


@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    print(f"inside upload_file received request {request}")
    uploaded_file = request.files['document']
    file_id = request.form['file_id']
    user_id = get_jwt_identity() #resolves the JWT token to get the user_id
    print(f"inside upload_file with user_id {user_id}")


    if not user_id:
        raise ValueError('user id is missing')
        return 'Session ID is missing or incorrect.', 400

 
    logger.info(
        f"uploading file {uploaded_file.filename} with id {file_id} for user {user_id} ")
    
    if uploaded_file:
        with redirect_stdout_to_logger(logger):
            # add file to Pinecone
            filepath = save_file_to_temp(uploaded_file)
            filename_only = os.path.basename(filepath)
            # must have a unique file_id, even if the file is the same per user

            logger.info(
                f"uploading file_name_only {filename_only} with id {file_id} for user jwt= {user_id} ")
            
            save_file_to_Pinecone_metadata(
                filepath, file_id, user_id, vectorstore)
            os.remove(filepath)

            # add file to docsource database
            description = 'File uploaded by user'  # might need to change
            docsource = DocSource(user_id=user_id, description=description,
                                filename=filename_only)
            db.session.add(docsource)
            db.session.commit()

            return jsonify('File uploaded and saved to the database.', 200)
    else:
        return 'No file was uploaded.', 400


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

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            session_id = auth_header[7:]
        logger.info(
            f"question: {question} for user {session.get('user_id', None)} with sid {session_id} ")
        with redirect_stdout_to_logger(logger):
            result = ask_question(question, vectorstore,
                                  chain, chat_history, session_id)
            print("qa result is", result)

        # Combine the `processed_text
        # ` and `page_content` JSON objects into a single dictionary
        print(result)
        return jsonify(result)

    except Exception as e:
        # Log the full traceback of the exception
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/delete_vector', methods=['POST'])
def delete_vector():
    print(f"deleting vector for user {session.get('user_id', None)} with sid {request.headers.get('Authorization')}")

    # delete vector from Pinecone database 
    # vectorstore._index.delete(filter = {'sid': request.headers.get('Authorization')})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)
