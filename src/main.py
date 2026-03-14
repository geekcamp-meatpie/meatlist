from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import streamlit as st
from fastapi.responses import FileResponse


from .llm import generate_todo_list
from .ocr import photo_capture
#from .utils import is_allowed_file

app = FastAPI(
    title="Meatlist API",
    description="meatpie_API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 
file_data: list[bytes] = []
count = 0


@app.post("/post_filepath")
async def upload_image(file: UploadFile = File(...)):
    global count
    contents = await file.read()
    file_data.append(contents)
    with open(f"image_{count}.png", "wb") as f:
        f.write(contents)
    count += 1

    return {"filename": file.filename}
@app.get("/download")
async def download():
    if not file_data:
        raise HTTPException(status_code=404, detail="No file")

    return {"byte": file_data[-1]}
@app.get("/return_json/{count}")
async def return_json():
    text = photo_capture(f"image_{count}.png")
    json = generate_todo_list(text)
    return json

