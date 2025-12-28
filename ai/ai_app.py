from rag_functions import load_and_process_document, create_rag_chain
from langchain.llms import Ollama

# Store global chain after document upload
GLOBAL_QA_CHAIN = None

def process_file(file_path):
    global GLOBAL_QA_CHAIN

    # Load PDF and get vectorstore
    vectorstore = load_and_process_document(file_path)

    # Create RAG chain with this vectorstore
    GLOBAL_QA_CHAIN = create_rag_chain(vectorstore)

    return "Document loaded successfully."

def ask_question(question):
    global GLOBAL_QA_CHAIN

    # If no PDF uploaded → use general AI
    if GLOBAL_QA_CHAIN is None:
        llm = Ollama(model="gpt-oss:20b-cloud")
        return llm(question)

    # If PDF uploaded → use RAG chain
    try:
        return GLOBAL_QA_CHAIN.run(question)
    except Exception as e:
        return f"Error processing question: {e}"
