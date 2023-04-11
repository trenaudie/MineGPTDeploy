from langchain.chains.chat_vector_db.prompts import (
    CONDENSE_QUESTION_PROMPT, QA_PROMPT)

from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import ConversationalRetrievalChain

from langchain.chains import LLMChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chat_models import ChatOpenAI
import os


def createchain(vectorstore):
    """Create a ConversationalRetrievalChain for question/answering."""

    llm = ChatOpenAI(
        openai_api_key=os.environ['OPENAI_API_KEY'],
        temperature=0,
        model_name='gpt-3.5-turbo'
    )

    # 1. question + history -> question2
    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
    # 1. q2 (+ history?) + sources -> [answers with sources] ->  one answer with sources
    doc_chain = load_qa_with_sources_chain(llm, chain_type="map_reduce")
    doc_chain.return_intermediate_steps = True
    chain = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        question_generator=question_generator,
        combine_docs_chain=doc_chain, return_source_documents=True)
    return chain
