# routes/notes.py
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from bson import ObjectId
from models.note import Note
from schemas.note import noteEntity, notesEntity
from config.db import conn

note = APIRouter()
templates = Jinja2Templates(directory="templates")

# Home route
@note.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    docs = conn.notes.notes.find({})
    newDocs = []
    for doc in docs:
        newDocs.append({
            "id": str(doc["_id"]),
            "title": doc["title"],
            "desc": doc["desc"]
        })
    return templates.TemplateResponse("index.html", {"request": request, "newDocs": newDocs})

# Get all notes route
@note.get("/get_all_notes")
async def get_all(request: Request):
    docs = conn.notes.notes.find({})
    return notesEntity(docs)

# About page route
@note.get("/about", response_class=HTMLResponse)
async def display_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# Add note to db
@note.post("/")
async def add_note(request: Request):
    form = await request.form()
    note = {
        "title": form.get("title"),
        "desc": form.get("desc")
    }
    result = conn.notes.notes.insert_one(note)
    return {"msg": "Note has been added successfully.", "id": str(result.inserted_id)}

# Read a single note by ID
@note.get("/{id}")
async def read_note(id: str):
    doc = conn.notes.notes.find_one({"_id": ObjectId(id)})
    if doc:
        return noteEntity(doc)
    raise HTTPException(status_code=404, detail="Note not found")

# Update a note by ID
@note.put("/{id}")
async def update_note(id: str, note: Note):
    result = conn.notes.notes.update_one({"_id": ObjectId(id)}, {"$set": dict(note)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"msg": "Note has been updated successfully"}

# Delete a note by ID
@note.delete("/{id}")
async def delete_note(id: str):
    result = conn.notes.notes.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"msg": "Note has been deleted successfully"}