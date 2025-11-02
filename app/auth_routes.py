from fastapi import APIRouter, HTTPException, Form
from jose import jwt #WT (JSON Web Token) is a compact, signed token the server gives a client after login. The client sends it on subsequent requests (in your frontend you included it as token in forms)
from datetime import datetime, timedelta,timezone
from .db import create_user, verify_user
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

#SECRET_KEY signs tokens; keep it secret (environment variable in production).
SECRET_KEY = os.getenv("SECRET_KEY")  # change in prod
ALGORITHM = "HS256"

def create_jwt(username: str):
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) #The returned string is the token the frontend stores and re-sends

@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    success = create_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if not verify_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(username)
    return {"access_token": token, "token_type": "bearer"}
