

from langchain.vectorstores import Pinecone
from langchain.chains import ConversationalRetrievalChain

def ask_question(question: str, vectorstore: Pinecone, chain: ConversationalRetrievalChain, chat_history: list[dict] = None) -> dict:
    """
    Use a question and the chat history to return the answer and the source documents.

    Updates chat history with the question and answer.

    Returns:
    dict with keys "answer", "sources"
    - answer: str
    - sources: list of dicts
        - filename: str
        - text: str
        - page: str (not yet implemented)
        - etc.
    :param question: The question to be answered.
    :param vectorstore: A Pinecone vectorstore object.
    :param chain: A ConversationalRetrievalChain object.
    :param chat_history: A list of dictionaries representing the chat history.
    :return: A dictionary containing the answer and the source documents.
    """

    result = chain({"question": question, "chat_history": chat_history})
    chat_history.append({"question": question, "answer": result["answer"]})
    answer = result['answer']
    sources = []

    for sourcedoc in result['source_documents']:
        sources.append({'filename' : sourcedoc.metadata['source'], 'text': sourcedoc.page_content})
    return {"answer": answer, "sources":sources}