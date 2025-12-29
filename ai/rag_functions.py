from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
import os

VECTORSTORE_DIR = "ai/vectorstore"
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

# Custom prompt for main points / concise answers
MAIN_POINTS_PROMPT = PromptTemplate(
    template="""
You are an AI assistant. 
Given the following context from a PDF document, extract the main points in a concise bullet-point format.

Context:
{context}

Main points:
""",
    input_variables=["context"]
)

def load_and_process_document(file_path):
    """
    Load PDF → Split → Embed → Save in Chroma → Return vectorstore
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    if not docs:
        raise ValueError("No text detected in PDF.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR
    )
    db.persist()
    return db


def create_rag_chain(vectorstore):
    """
    Create a RetrievalQA using the SPECIFIC vectorstore of the uploaded PDF
    """
    retriever = vectorstore.as_retriever(search_kwargs={"k": 20})  # increase k for more coverage
    llm = Ollama(model="llama3")

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": MAIN_POINTS_PROMPT},
        return_source_documents=False
    )
    return qa


















