from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

# 1️⃣ Load document
loader = TextLoader("docs/sample.txt")  
docs = loader.load()

# 2️⃣ Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

# 3️⃣ Create embeddings
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# 4️⃣ Create vector store
vectordb = Chroma.from_documents(chunks, embeddings)

# 5️⃣ Create RetrievalQA chain
llm = Ollama(model="llama3")
qa = RetrievalQA.from_chain_type(llm=llm, retriever=vectordb.as_retriever())

print("✅ Chatbot ready! Ask questions about your document. Type 'exit' to quit.")

while True:
    query = input("\nAsk: ")
    if query.lower() == "exit":
        break
    answer = qa.invoke(query)
    print("Answer:", answer['result'])