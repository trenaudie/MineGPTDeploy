import os
import PyPDF2
from langchain.schema import Document

from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
from werkzeug.datastructures import FileStorage

from utils.redirect_stdout import redirect_stdout_to_logger
from utils.logger import logger
from werkzeug.utils import secure_filename


def getDocs():
    """Returns list of Document() objects from articles.txt files"""
    for file in os.listdir():
        if file.endswith(".txt"):
            with open(file, "r") as f:
                github_url = f"{file}"
                yield Document(page_content=f.read(), metadata={"source": github_url})


def saveChunksToStore(search_index, contentdict):
    """Returns list of Document() objects from {file:filecontent} dictionary"""
    splitter = CharacterTextSplitter(
        separator=" ", chunk_size=512, chunk_overlap=0)
    sources = []

    for file in contentdict.keys():
        sourcename = file
        sources.append(
            Document(page_content=contentdict[file], metadata={"source": sourcename}))

    textchunks = []
    for source in sources:
        sourcename = file
        for chunk in splitter.split_text(source.page_content):
            textchunks.append(
                Document(page_content=chunk, metadata=source.metadata.copy()))

    # what about first search index
    search_index.add_documents(textchunks)
    search_index.persist()



def save_file_to_temp(uploaded_file: FileStorage):
    """Prototype function that simply saves one file to the temp directory
    Returns: filepath : str eg. 'temp/abc.pdf"""
    filename = secure_filename(uploaded_file.filename)
    filepath = os.path.join('temp', filename)
    uploaded_file.save(filepath)



def save_file_to_Pinecone(filepath:str, vectorstore:Pinecone):
    """Reads one file from the temp directory (pdf and .txt files supported) then splits and saves to Pinecone"""

    filename, file_extension = os.path.splitext(filepath)
    filename.replace("\\temp", "")
    if file_extension.lower() == '.pdf':
        pdf_reader = PyPDF2.PdfReader(filepath)
        content = ""

        for page in pdf_reader.pages:
            content += page.extract_text()

    elif file_extension.lower() == '.txt':
        with open(filepath, 'r') as file:
            content = file.read()
    else:
        raise ValueError(f"Invalid file type: {filepath}. Only PDF and text files are supported.")

    #write from filepath, content to Pinecone
    chunksize = 512 #important parameter
    source = {"page_content":content, "metadata":{source:filepath}}
    source_chunks = []
    splitter = CharacterTextSplitter(separator=" ", chunk_size=chunksize, chunk_overlap=0)
    for chunk in (splitter.split_text(source.get("page_content"))):
        newdoc = Document(page_content=chunk, metadata=source.get('metadata').copy())
        source_chunks.append(newdoc)
    with redirect_stdout_to_logger(logger):
        indexes = vectorstore.add_documents(source_chunks)
    indexes = vectorstore.add_documents(source_chunks)
    logger.info(f"added to vectorstore {len(source_chunks)} chunks from {filepath}")
    logger.info(f"vectorstore stats: {vectorstore._index.describe_index_stats()}")



