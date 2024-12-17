from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import shutil
from datetime import datetime
from typing import List, Dict
import uvicorn

from .ai.object_recognition import ObjectRecognitionModule, IndigenousTermMapper
from .schemas import (
    DetectionResponse,
    TermResponse,
    ProcessImageResponse,
    LanguageCreate,
    TermCreate
)

app = FastAPI(title="LinguaLearn API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
object_recognition = ObjectRecognitionModule()
term_mapper = IndigenousTermMapper("xhosa")

@app.post("/api/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        temp_path = f"temp/{datetime.now().timestamp()}_{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
        
        detections = object_recognition.process_image(temp_path)
        
        for detection in detections:
            detection['indigenousTerm'] = term_mapper.get_indigenous_term(detection['label'])
        
        return {"success": True, "detections": detections}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)