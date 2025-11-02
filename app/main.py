from fastapi import FastAPI
from app.auth_routes import router as auth_router
from app.chat_routes import router as chat_router

app = FastAPI(title="Multi-User RAG Chatbot")
app.include_router(auth_router)
app.include_router(chat_router)

"""
This imports the FastAPI framework — it’s what creates and runs the web API server.
Think of FastAPI() as your main server object that will:

Listen for incoming HTTP requests (like /login, /register, /chat, etc.)

Match those requests to your defined endpoints (from route files)

Handle responses (JSON, errors, etc.)
"""

"""
So what happens when you run uvicorn main:app?

FastAPI loads this file and creates app.

Routers from authentication and chat are attached.

Uvicorn runs the app on a port (e.g., http://127.0.0.1:8000).

You can now hit endpoints like:

POST /auth/register

POST /auth/login

POST /chat/upload

POST /chat/query
"""