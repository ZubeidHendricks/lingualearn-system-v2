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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI modules
object_recognition = ObjectRecognitionModule()
term_mapper = IndigenousTermMapper("xhosa")  # Default language

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/lingualearn")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.post("/api/process-image", response_model=ProcessImageResponse)
async def process_image(file: UploadFile = File(...)):
    """Process uploaded image and return detected objects with indigenous terms."""
    try:
        # Save uploaded file
        temp_path = f"temp/{datetime.now().timestamp()}_{file.filename}"
        os.makedirs("temp", exist_ok=True)
        
        with open(temp_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
        
        # Process image with AI module
        detections = object_recognition.process_image(temp_path)
        
        # Add indigenous terms to detections
        for detection in detections:
            detection['indigenousTerm'] = term_mapper.get_indigenous_term(detection['label'])
        
        # Save to database
        with SessionLocal() as db:
            # Save image record
            query = text("""
                INSERT INTO captured_images (file_path, processed, metadata)
                VALUES (:path, true, :metadata)
                RETURNING id
            """)
            result = db.execute(query, {
                'path': temp_path,
                'metadata': {'original_filename': file.filename}
            })
            image_id = result.fetchone()[0]
            
            # Save detections
            for detection in detections:
                query = text("""
                    INSERT INTO object_detections (image_id, confidence, bbox_coordinates)
                    VALUES (:image_id, :confidence, :bbox)
                """)
                db.execute(query, {
                    'image_id': image_id,
                    'confidence': detection['confidence'],
                    'bbox': detection['bbox']
                })
            
            db.commit()
        
        return ProcessImageResponse(
            success=True,
            detections=detections,
            image_id=image_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/languages", response_model=Dict)
async def add_language(language: LanguageCreate):
    """Add a new language to the system."""
    with SessionLocal() as db:
        query = text("""
            INSERT INTO languages (code, name, region)
            VALUES (:code, :name, :region)
            RETURNING id, code, name
        """)
        result = db.execute(query, language.dict())
        db.commit()
        return dict(result.fetchone())

@app.post("/api/terms", response_model=Dict)
async def add_term(term: TermCreate):
    """Add a new indigenous term."""
    with SessionLocal() as db:
        query = text("""
            INSERT INTO indigenous_terms (language_id, object_id, term, pronunciation, context)
            VALUES (:language_id, :object_id, :term, :pronunciation, :context)
            RETURNING id, term
        """)
        result = db.execute(query, term.dict())
        db.commit()
        return dict(result.fetchone())

@app.get("/api/terms/{language_code}", response_model=List[TermResponse])
async def get_terms(language_code: str):
    """Get all terms for a specific language."""
    with SessionLocal() as db:
        query = text("""
            SELECT t.*, l.code as language_code, o.label as object_label
            FROM indigenous_terms t
            JOIN languages l ON t.language_id = l.id
            JOIN objects o ON t.object_id = o.id
            WHERE l.code = :language_code
        """)
        result = db.execute(query, {'language_code': language_code})
        return [dict(row) for row in result]

@app.get("/api/statistics", response_model=Dict)
async def get_statistics():
    """Get system statistics."""
    with SessionLocal() as db:
        stats = {
            'total_images': db.execute(text("SELECT COUNT(*) FROM captured_images")).scalar(),
            'total_terms': db.execute(text("SELECT COUNT(*) FROM indigenous_terms")).scalar(),
            'total_languages': db.execute(text("SELECT COUNT(*) FROM languages")).scalar(),
            'recent_contributions': db.execute(text("""
                SELECT COUNT(*) FROM user_contributions 
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """)).scalar()
        }
        return stats

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)