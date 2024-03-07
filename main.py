from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Union
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import sqlite3
from chatbot.chatbot import Chatbot
import os

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def create_users_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            full_name TEXT,
            email TEXT,
            hashed_password TEXT,
            disabled INTEGER
        )
    ''')
    conn.commit()
    conn.close()

create_users_table()
# Function to create a new SQLite connection
def create_connection():
    return sqlite3.connect("users.db")

# Function to create a new cursor from a connection
def create_cursor(conn):
    return conn.cursor()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class BotQuery(BaseModel):
    query_text: str
    # stream = bool
class BotResponse(BaseModel):
    response: str
class UserInDB(User):
    hashed_password: str

# Function to verify the password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to hash the password
def get_password_hash(password):
    return pwd_context.hash(password)

# Function to get a user from the database by username
def get_user(conn, username: str):
    cursor = create_cursor(conn)
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    result = cursor.fetchone()
    if result:
        return UserInDB(username=result[1], email=result[3], full_name=result[2], hashed_password=result[4], disabled=bool(result[5]))

# Function to authenticate a user
def authenticate_user(conn, username: str, password: str):
    user = get_user(conn, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Function to create an access token
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get the current user from the token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    conn = create_connection()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(conn, token_data.username)
    if user is None:
        raise credentials_exception
    conn.close()
    return user
    # finally:
    

# Dependency to get the current active user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = create_connection()
    user = authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    conn.close()
    return {"access_token": access_token, "token_type": "bearer"}

class UserCreate(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    password: str

@app.post("/users/create", response_model=User)
def create_user(user: UserCreate):
    conn = create_connection()
    cursor = create_cursor(conn)
    cursor.execute('''
        INSERT INTO users (username, full_name, email, hashed_password, disabled)
        VALUES (?, ?, ?, ?, ?)
    ''', (user.username, user.full_name, user.email, get_password_hash(user.password), False))
    conn.commit()
    result = get_user(conn, user.username)
    conn.close()
    return result

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


llm = Chatbot()
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from py_trans import Async_PyTranslator

tr = Async_PyTranslator()

async def generator(query: str, session_id: str, internet_search:bool) -> AsyncGenerator[str, None]:
    content = ""
    query = await tr.translate_dict(query, "en")
    print(query)
    for chunk in llm.stream(query['translation'], session_id, internet_search=internet_search):
        content += chunk
        if "\n" in chunk:
            res =  await tr.translate_dict(content, "vi")
            yield res['translation']+'\n'
            content = ""
    if content != "":
        res =  await tr.translate_dict(content, "vi")
        yield res['translation']+'\n'

@app.get("/chat/")
async def chat(query: str,internet_search: bool, current_user: User = Depends(get_current_active_user), session_id: str = ""):
    if session_id == "":
        session_id = current_user.username
    return StreamingResponse(generator(query, session_id, internet_search))
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8055)