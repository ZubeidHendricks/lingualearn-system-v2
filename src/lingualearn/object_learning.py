from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ObjectTerm:
    object_name: str          # Standard/formal name
    local_term: str          # Local slang/term
    language: str            # Language code
    region: Optional[str]    # Geographic region
    context: Optional[str]   # Usage context
    dialect: Optional[str]   # Specific dialect
    image_hash: str         # Hash of reference image
    confidence: float = 0.5
    added_by: Optional[str] = None  # Linguist ID who added it
    verified: bool = False

class ObjectLearner:
    def __init__(self, db_path: str = 'object_terms.db'):
        self.db_path = db_path
        self._init_database()
        
        # Initialize object detection model
        self.object_detector = cv2.dnn_DetectionModel('yolov4-tiny.weights', 'yolov4-tiny.cfg')
        self.object_detector.setInputParams(size=(416, 416), scale=1/255)
        
        # Minimum confidence for object detection
        self.detection_threshold = 0.6

    def _init_database(self) -> None:
        """Initialize SQLite database for storing object terms"""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS object_terms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    object_name TEXT NOT NULL,
                    local_term TEXT NOT NULL,
                    language TEXT NOT NULL,
                    region TEXT,
                    context TEXT,
                    dialect TEXT,
                    image_hash TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    added_by TEXT,
                    verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(local_term, language, dialect)
                )
            """)

    async def learn_object_term(self, frame: np.ndarray, term: ObjectTerm) -> Dict[str, any]:
        """Learn a new object term from camera frame"""
        # Detect objects in frame
        classes, scores, boxes = self.object_detector.detect(frame)
        
        if len(boxes) == 0:
            return {
                'success': False,
                'error': 'No objects detected in frame'
            }

        # Get the most prominent object (highest confidence)
        best_idx = np.argmax(scores)
        if scores[best_idx] < self.detection_threshold:
            return {
                'success': False,
                'error': 'Object detection confidence too low'
            }

        # Generate image hash for the detected object region
        box = boxes[best_idx]
        object_img = frame[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
        image_hash = self._compute_image_hash(object_img)
        
        # Store the term with the image hash
        term.image_hash = image_hash
        await self._store_term(term)

        return {
            'success': True,
            'object_class': classes[best_idx],
            'confidence': float(scores[best_idx]),
            'term': term
        }

    async def identify_object(self, frame: np.ndarray, language: str) -> List[ObjectTerm]:
        """Identify object in frame and return known local terms"""
        # Detect objects
        classes, scores, boxes = self.object_detector.detect(frame)
        
        if len(boxes) == 0:
            return []

        # Get the most prominent object
        best_idx = np.argmax(scores)
        if scores[best_idx] < self.detection_threshold:
            return []

        # Get image hash
        box = boxes[best_idx]
        object_img = frame[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
        image_hash = self._compute_image_hash(object_img)
        
        # Find matching terms
        return await self._find_terms(image_hash, language)

    def _compute_image_hash(self, image: np.ndarray) -> str:
        """Compute perceptual hash of image for matching"""
        # Resize image to 8x8
        img = cv2.resize(image, (8, 8))
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Compute DCT
        dct = cv2.dct(np.float32(gray))
        # Compute hash
        dct_low = dct[:8, :8]
        avg = dct_low.mean()
        diff = dct_low > avg
        # Convert boolean array to hash string
        return ''.join(['1' if b else '0' for b in diff.flatten()])

    async def _store_term(self, term: ObjectTerm) -> None:
        """Store object term in database"""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO object_terms
                (object_name, local_term, language, region, context, dialect,
                 image_hash, confidence, added_by, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                term.object_name,
                term.local_term,
                term.language,
                term.region,
                term.context,
                term.dialect,
                term.image_hash,
                term.confidence,
                term.added_by,
                term.verified
            ))

    async def _find_terms(self, image_hash: str, language: str) -> List[ObjectTerm]:
        """Find matching terms for an image hash in a specific language"""
        import sqlite3
        terms = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM object_terms
                WHERE language = ? AND
                      (image_hash = ? OR
                       ABS(CAST(image_hash AS INTEGER) - CAST(? AS INTEGER)) < 10)
                ORDER BY confidence DESC
            """, (language, image_hash, image_hash))
            
            for row in cursor.fetchall():
                terms.append(ObjectTerm(
                    object_name=row[1],
                    local_term=row[2],
                    language=row[3],
                    region=row[4],
                    context=row[5],
                    dialect=row[6],
                    image_hash=row[7],
                    confidence=row[8],
                    added_by=row[9],
                    verified=row[10]
                ))
                
        return terms