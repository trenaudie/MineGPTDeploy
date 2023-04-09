from getchain import get_chain
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import os
import traceback
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import json
from config import Config
from flask_cors import CORS

from utils.logger import logger
from utils.ingest import save_file_to_database

os.environ['OPENAI_API_KEY'] = Config.openai_api_key
print(os.environ['OPENAI_API_KEY'])
os.environ['HUGGINGFACEHUB_API_TOKEN'] = Config.huggingface_hub_api_key

def getattributes(obj): return [attr for attr in dir(
    obj) if attr.startswith('__') is False]


app = Flask(__name__)
CORS(app,  origins = ["http://localhost:3000"])


prompt_template = """Use the context below to write a 100 word blog post about the topic below:
    Context: {context}
    Topic: {topic}
    Blog post:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "topic"]
)

chat_history = []
list_of_files = ['file1', 'file2', 'file3', 'file4']
vectordb = Chroma(persist_directory='dbdir',
                  embedding_function=OpenAIEmbeddings())
chain = get_chain(vectordb, PROMPT)
print(vectordb._collection.metadata)


@app.route('/')
def index():
    return "hello world"


@app.route('/upload', methods=['POST'])
def upload_file():
    print("received upload request")
    uploaded_file = request.files['document']
    file_id = request.form['id']
    if uploaded_file:
        # Save the file temporarily
        filename = secure_filename(uploaded_file.filename)
        list_of_files.append(filename)
        #save the file to a database:
        filepath = os.path.join('temp', filename)
        uploaded_file.save(filepath)

        #embed the vectors in a database eg Pinecone
        save_file_to_database(vectordb, filepath)
        logger.info(
            f"number of documents in db: {vectordb._collection._client._count('langchain')}")
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
        answer = chain({'question': question, 'chat_history': chat_history})
        chat_history.append((question, answer['answer']))

        # for k in chat_history:
        #     logger.info(k)
        logger.info(f"(question, answer['answer']) = {question, answer['answer']}")
        logger.info('sources')
        for sourceDoc in answer['source_documents']:
            logger.info(sourceDoc.page_content[:10])
        logger.info('-----------------')
        source_contents = [
            sourceDoc.page_content for sourceDoc in answer['source_documents']]

        # Convert the list of page contents to a JSON object

        # Combine the `processed_text` and `page_content` JSON objects into a single dictionary
        response_data = {
            'answer': answer['answer'],
            'source_documents': source_contents
        }
        return jsonify(response_data)

    except Exception as e:
        # Log the full traceback of the exception
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5006, debug=True)
