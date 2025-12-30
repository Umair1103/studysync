from rag_functions import load_and_process_document, create_rag_chain
from langchain.llms import Ollama

# Store global chain after document upload
GLOBAL_QA_CHAIN = None


def process_file(file_path):
    global GLOBAL_QA_CHAIN

    vectorstore = load_and_process_document(file_path)
    GLOBAL_QA_CHAIN = create_rag_chain(vectorstore)

    return "Document loaded successfully."


def ask_question(question):
    global GLOBAL_QA_CHAIN

    # 🔒 Force English
    prompt = f"Answer ONLY in English.\n\n{question}"

    # No PDF → general AI
    if GLOBAL_QA_CHAIN is None:
        llm = Ollama(model="gpt-oss:20b-cloud")
        return llm(prompt)

    # PDF uploaded → RAG
    try:
        return GLOBAL_QA_CHAIN.run(prompt)
    except Exception as e:
        return f"Error processing question: {e}"
