import os, json, traceback

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

from utils.logger import logger
from utils.ingest import save_file_to_Pinecone, save_file_to_temp
from utils.ask_question import ask_question
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
vectorstore = Pinecone.from_existing_index(index_name, embedding=OpenAIEmbeddings())


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
CORS(app,  origins=["http://localhost:3000"])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


prompt_template = """Use the context below to write a 100 word blog post about the topic below:
    Context: {context}
    Topic: {topic}
    Blog post:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "topic"]
)

chat_history = []
list_of_files = ['file1', 'file2', 'file3', 'file4']
chain = createchain(vectorstore, PROMPT)


@app.route('/')
def index():
    return "hello world"


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    if email[-22] == '@etu.minesparis.psl.eu':
        password = generate_password_hash(
            request.form['password'], method='sha256')
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return 'registration successful!', 200
    else:
        return 'failed registration', 400


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return 'authenticated'
    return 'incorrect authentification'


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
def upload_file():
    print("received upload request")
    uploaded_file = request.files['document']
    file_id = request.form['id']
    if uploaded_file:
        filepath = uploaded_file.save(uploaded_file)
        save_file_to_temp(filepath)
        # embed the vectors in a database eg Pinecone
        save_file_to_Pinecone(vectorstore, filepath)
        logger.info(
            f"number of documents in db: {vectorstore._index.describe_index_stats()}")
        # Remove the temporary file
        os.remove(filepath)
        return 'File uploaded and saved to the database.', 200
    else:
        return 'No file was uploaded.', 400


# @app.route('/update_file_list')
# def update_file_list():
#     list_of_files = read_file_list()

#     return jsonify({'lines': list_of_files})


@app.route('/qa', methods=['POST'])
def answerQuestion():
    try:
        question = request.form['searchTerm']
        # only add chat_history if conversationalRetriever
        # answer = chain({'question': question, 'chat_history': chat_history})
        # chat_history.append((question, answer['answer']))

        # for k in chat_history:
        #     logger.info(k)
        result = ask_question(question, vectorstore, chat_history, chain)
        logger.info(
            f"(question, answer['answer']) = {question, result['answer']}")
        logger.info('sources')
        for source in result['sources']:
            logger.info(source['filename'])
            logger.info(source['text'])
        # Convert the list of page contents to a JSON object

        # Combine the `processed_text` and `page_content` JSON objects into a single dictionary
        return jsonify(result)

    except Exception as e:
        # Log the full traceback of the exception
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5006, debug=True)
