# multiuser_article-pdf_rag_chatbot
This project combines LLMs, RAG (Retrieval-Augmented Generation), authentication, and a full-stack interface — to create a personalized AI chatbot where each user can upload research papers or URLs and chat with their own data.
🧠 Multi-User RAG Chatbot (FastAPI + Streamlit)

A complete end-to-end Retrieval-Augmented Generation (RAG) chatbot system supporting multiple users, each with their own context, vector database, and chat history.

This project allows users to:

Register & log in (JWT-based authentication)

Upload research papers (PDF or URL)

Ask contextual questions using Llama-3.1-8B-Instruct

Store their own chat history & document embeddings

🚀 Tech Stack
Layer	Tools
Backend API	FastAPI
Frontend	Streamlit
Vector Store	ChromaDB
Embeddings	MiniLM (Hugging Face)
Model	Llama-3.1-8B-Instruct via Hugging Face Hub
Auth	SQLite + bcrypt + JWT
Loader	LangChain PyPDFLoader & WebBaseLoader

🧱 Features
🔐 1. User Authentication

Register new users with hashed passwords (passlib[bcrypt]).

Log in to get a JWT token (used for all subsequent requests).

Each user gets their own isolated folder under ./user_data/{username}/.

📄 2. Document Upload

Upload research articles via URL or PDF.

PDFs are temporarily saved and parsed using LangChain’s PyPDFLoader.

Content is split into chunks and stored in a Chroma vector DB for the user.

💬 3. Chat Interface

Uses Llama-3.1-8B-Instruct via Hugging Face API.

Context-aware responses using:

Retrieved chunks from user’s documents

Long-term chat memory stored in Chroma

Short-term chat buffer memory

Streamlit UI shows clean chat threads and user session management.

👥 4. Multi-User Isolation

Each user’s context and chat history are stored separately under:

./user_data/{username}/context_VDB/
./user_data/{username}/chat_history_VDB/


Prevents overlap or data leaks between users.

⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/multi-user-rag-chatbot.git
cd multi-user-rag-chatbot

2️⃣ Create and Activate a Virtual Environment
python -m venv rag_env
source rag_env/bin/activate  # or rag_env\Scripts\activate on Windows

3️⃣ Install Requirements
pip install -r requirements.txt

4️⃣ Set Environment Variables

Create a .env file or export manually:

HUGGINGFACEHUB_API_TOKEN=<your_huggingface_token>
secrete_key=<your_fastapi_secret_key>

5️⃣ Run the FastAPI Backend
uvicorn main:app --reload

6️⃣ Run the Streamlit Frontend
streamlit run app.py


🧠 How It Works (Flow)

User registers / logs in → gets JWT token

User uploads PDF / URL → vector embeddings stored under user_data/{username}/

User chats → chatbot retrieves relevant context and chat history → generates a contextual answer

Each user’s sessions remain isolated