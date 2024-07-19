from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta

app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["note_master"]
users_collection = db["users"]
notes_collection = db["notes"]

# JWT and password management
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if (user := db["users"].find_one({"username": username})) is not None:
        return UserInDB(**user)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(users_collection, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=30)
    access_token = jwt.encode({"sub": user.username, "exp": datetime.utcnow() + access_token_expires}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup")
async def signup(user: User):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    user.hashed_password = get_password_hash(user.password)
    users_collection.insert_one(user.dict())
    return {"msg": "User created"}

@app.get("/notes")
async def get_notes(token: str = Depends(oauth2_scheme)):
    verify_token(token)
    notes = notes_collection.find({})
    return {"notes": list(notes)}

@app.post("/notes")
async def create_note(note: dict, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    notes_collection.insert_one(note)
    return {"msg": "Note added"}

@app.put("/notes/{note_id}")
async def update_note(note_id: str, note: dict, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    notes_collection.update_one({"_id": note_id}, {"$set": note})
    return {"msg": "Note updated"}

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    notes_collection.delete_one({"_id": note_id})
    return {"msg": "Note deleted"}
