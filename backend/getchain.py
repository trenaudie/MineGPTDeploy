
"""Create a ChatVectorDBChain for question/answering."""
from langchain.callbacks.base import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import ChatVectorDBChain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT,
                                                     QA_PROMPT)
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.vectorstores.base import VectorStore
from langchain import HuggingFaceHub
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains import ConversationalRetrievalChain

from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.prompts import PromptTemplate
from langchain.llms import GPT4All


def get_chain(vectorstore: VectorStore, prompt: PromptTemplate) -> ChatVectorDBChain:
    # qa_chain = load_qa_with_sources_chain(OpenAI(), chain_type="stuff")
    # qa = RetrievalQAWithSourcesChain(combine_documents_chain=qa_chain, retriever=vectorstore.as_retriever())
    llmHugging = HuggingFaceHub(
        repo_id="google/flan-t5-xl", model_kwargs={"temperature": 0, "max_length": 128})
    #path_to_ggml = "/Users/tanguyrenaudie/Documents/TanguyML/gpt4all_model/gpt4all-converted.bin"
    #llmGPT4all = GPT4All(model=path_to_ggml)
    openai = OpenAI()
    qa = ConversationalRetrievalChain.from_llm(
        llmHugging, vectorstore.as_retriever(), return_source_documents=True)
    return qa
