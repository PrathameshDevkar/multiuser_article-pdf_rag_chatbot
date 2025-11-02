from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException, File
from jose import jwt, JWTError
from .rag_util import *
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.output_parsers import StrOutputParser
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

"""
Handles all RAG logic and chat endpoints:
- /upload_url: saves webpage content into user's vector store
- /upload_pdf: saves uploaded PDF content into user's vector store
- /chat: runs retrieval-augmented chat using HuggingFace LLM
"""


load_dotenv()

router = APIRouter()
hf_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
def get_username_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/upload_url")
async def upload_url(token: str = Form(...), url: str = Form(...)):
    username = get_username_from_token(token)
    docs = load_article_from_url(url)
    chunks = split_docs(docs)
    context_vdb = context_VDB(username)
    context_vectordb(context_vdb, chunks)
    return {"message": f"Context saved for user {username}"}

@router.post("/upload_pdf")
async def upload_pdf_path(token: str = Form(...), file: UploadFile = File(...)):
    username = get_username_from_token(token)
    if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    # Read the file bytes
    
    contents = await file.read()

    user_folder = f"./user_data/{username}"
    import os
    os.makedirs(user_folder, exist_ok=True)
    temp_pdf_path = os.path.join(user_folder, file.filename)
    with open(temp_pdf_path, "wb") as f:
        f.write(contents)

        # Load PDF via LangChain PyPDFLoader (expects file path)
    docs = load_article_from_pdf(temp_pdf_path)    
    chunks = split_docs(docs)
    context_vdb = context_VDB(username)
    context_vectordb(context_vdb, chunks)
    os.remove(temp_pdf_path)

    return {"message": f"Context saved for user {username}"}

@router.post("/chat")
async def chat(token: str = Form(...), query: str = Form(...)):
    username = get_username_from_token(token)
    context_vdb = context_VDB(username)
    chat_vdb = chat_history_VDB(username)
    context_retriever = context_vdb.as_retriever(search_type="similarity", k=3)
    llm = HuggingFaceEndpoint(model="meta-llama/Llama-3.1-8B-Instruct", huggingfacehub_api_token=hf_api_key)
    model = ChatHuggingFace(llm=llm)
    parser = StrOutputParser()
    memory = ConversationBufferMemory(return_messages=True)
    prompt = PromptTemplate(
        template="""
        You are an AI assistant who answers based on the given context, 
        long-term and short-term chat history. If you don't know, say you don't know.
        Context:\n{context}\n
        Long-term chat history:\n{long_term_chat_history}\n
        Short-term chat history:\n{short_term_chat_history}\n
        User question: {query}\n
        """,
        input_variables=["query", "context", "long_term_chat_history", "short_term_chat_history"]
    )
    parallel_chain = RunnableParallel({
        "short_term_chat_history": RunnableLambda(lambda x: "\n".join([m.content for m in memory.chat_memory.messages[-5:]])),
        "long_term_chat_history": RunnableLambda(lambda x: retrieve_long_term_chat_history(chat_vdb, x)),
        "context": context_retriever | RunnableLambda(creating_context),
        "query": RunnablePassthrough()
    })
    final_chain = parallel_chain | prompt | model | parser
    response = final_chain.invoke(query)
    save_long_term_chat_history(chat_vdb, query, response)
    memory.chat_memory.add_user_message(query)
    memory.chat_memory.add_ai_message(response)
    return {"response": response}
