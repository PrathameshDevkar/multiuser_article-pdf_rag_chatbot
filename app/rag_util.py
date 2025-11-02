import os
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()
# ======================
# STEP 1 — Load data
# ======================

def load_article_from_url(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs

def load_article_from_pdf(path):
    print("==================inside load_article_from_pdf=========== ")
    loader = PyPDFLoader(path)
    docs = loader.load()
    print("==============docs are",docs)
    print("+==========================")
    return docs

# ======================
# STEP 2 — Split into chunks
# ======================

def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_documents(docs)

# ======================
# STEP 3 — Per-user Vector Stores
# ======================

def get_user_dirs(username):
    base_dir = f"./user_data/{username}"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(f"{base_dir}/context_VDB", exist_ok=True)
    os.makedirs(f"{base_dir}/chat_history_VDB", exist_ok=True)
    return base_dir

def chat_history_VDB(username):
    emb_model_path=os.getenv("EMBEDDING_MODEL_PATH")
    embeddings = HuggingFaceEmbeddings(model=emb_model_path)
    path = f"./user_data/{username}/chat_history_VDB"
    return Chroma(collection_name="chat_emb", embedding_function=embeddings, persist_directory=path)

def context_VDB(username):
    emb_model_path=os.getenv("EMBEDDING_MODEL_PATH")
    embeddings = HuggingFaceEmbeddings(model=emb_model_path)    
    path = f"./user_data/{username}/context_VDB"
    return Chroma(collection_name="context_emb", embedding_function=embeddings, persist_directory=path)

def context_vectordb(vector_store, chunks):
    vector_store.add_documents(chunks)
    return vector_store

def save_long_term_chat_history(chat_vector_store, user_query, ai_response):
    history = f"user: {user_query}\nAI: {ai_response}"
    doc = Document(page_content=history, metadata={"type": "conversation_turn"})
    chat_vector_store.add_documents([doc])

def retrieve_long_term_chat_history(chat_vector_store, user_query):
    docs = chat_vector_store.similarity_search(user_query, k=3)
    result = "\n\n".join([i.page_content for i in docs])
    return result

def creating_context(docs):
        context="\n".join([doc.page_content for doc in docs])
        return context