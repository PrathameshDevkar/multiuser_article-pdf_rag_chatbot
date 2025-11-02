import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #Creates a password hashing context using bcrypt (industry-standard)

def get_db():
    conn = sqlite3.connect("users.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    conn.commit()
    return conn

def create_user(username, password):
    conn = get_db()
    hashed = pwd_context.hash(password) #produces a salted hash.
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed)) #Executes parameterized INSERT ... VALUES (?, ?) to prevent SQL injection.
        conn.commit()
        return True
    except sqlite3.IntegrityError: #If username already exists, SQLite raises IntegrityError because username is UNIQUE; function returns False in that case, otherwise True.
        return False

def verify_user(username, password):
    conn = get_db()
    cursor = conn.execute("SELECT password FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if row and pwd_context.verify(password, row[0]): #checks a provided password
        return True
    return False
