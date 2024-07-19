from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes.note import note

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(note)