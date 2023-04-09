import os
import PyPDF2
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

from langchain.indexes import VectorstoreIndexCreator
# from utils.database_management import write_to_file_list

from utils.logger import logger


def getDocs():
    """Returns list of Document() objects from articles.txt files"""
    for file in os.listdir():
        if file.endswith(".txt"):
            with open(file, "r") as f:
                github_url = f"{file}"
                yield Document(page_content=f.read(), metadata={"source": github_url})


def saveChunksToStore(search_index: Chroma, contentdict):
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
                Document(page_content=chunk, metadata=source.metadata))

    # what about first search index
    search_index.add_documents(textchunks)
    search_index.persist()


def save_file_to_database(search_index: Chroma, filepath: str):
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
        print(
            f"Invalid file type: {filepath}. Only PDF and text files are supported.")
        raise ValueError("Invalid file type.")

    content_dict = {filepath: content}
    # write_to_file_list(filepath)

    saveChunksToStore(search_index, content_dict)
