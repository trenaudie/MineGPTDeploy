import os
import json
import traceback

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


from utils.logger import logger
from utils.ingest import save_file_to_Pinecone, save_file_to_temp
from utils.redirect_stdout import redirect_stdout_to_logger
from utils.ask_question import ask_question
from utils.printUsers import printUsers
from config import Config
from utils.getchain import createchain

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
app.config['SECRET_KEY'] = 'your_secret_key'
# Use 'redis' or 'memcached' for production
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600 * \
    3  # expired sessions are deleted after 3 hr

db = SQLAlchemy(app)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'session_files'
Session(app)
CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})


class DocSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    docsources = db.relationship('DocSource', backref='user', lazy=True)


chat_history = []
chain = createchain(vectorstore)


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
            return jsonify(status='registration successful!'), 200
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
    with redirect_stdout_to_logger(logger):
        printUsers(User)
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify(status='authenticated'), 200
    return jsonify(status='incorrect authentification'), 400


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.clear()
    return jsonify(status='logged out'), 200


@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['document']
    file_id = request.form['id']

    if 'user_id' not in session:
        return 'User not logged in.', 400

    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        save_file_to_temp(uploaded_file)
        filepath = os.path.join(Config.TEMP_FOLDER, filename)
        print(f"uploading filename {filename}, filepath {filepath}")
        save_file_to_Pinecone(filepath, vectorstore)
        os.remove(filepath)
        return 'File uploaded and saved to the database.', 200
    else:
        return 'No file was uploaded.', 400


# @app.route('/update_file_list')
# def update_file_list():
#     list_of_files = read_file_list()

#     return jsonify({'lines': list_of_files})

@app.route('/logout')
def logout():
    # Remove user data from the session
    try:
        session.pop('user_id', None)
        session.pop('username', None)
        return jsonify('logged out'), 200
    except:
        return jsonify('logged out'), 400


@app.route('/qa', methods=['POST'])
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
        question = request.form['question']

        with redirect_stdout_to_logger(logger):
            result = ask_question(question, vectorstore, chain, chat_history)

        logger.info(
            f"(question, answer['answer']) = {question, result['answer']}")
        logger.info('sources')
        for source in result['sources']:
            logger.info(source['filename'])
            logger.info(source['text'])

        # Combine the `processed_text` and `page_content` JSON objects into a single dictionary
        return jsonify(result)

    except Exception as e:
        # Log the full traceback of the exception
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000)
