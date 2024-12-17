import torch
import numpy as np
from segment_anything import sam_model_registry, SamPredictor
from PIL import Image
import io
import base64
from typing import List, Dict, Any

class ObjectDetector:
    def __init__(self, model_path: str = "models/sam_vit_h_4b8939.pth"):
        """Initialize the SAM model for object detection"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Initialize SAM
        self.sam = sam_model_registry["vit_h"](checkpoint=model_path)
        self.sam.to(device=self.device)
        self.predictor = SamPredictor(self.sam)
        
    def process_image(self, image_data: str) -> Image.Image:
        """Convert base64 image data to PIL Image"""
        try:
            # Remove data URL prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            return image.convert('RGB')
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    def detect_objects(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Detect objects in the image using SAM"""
        # Convert PIL Image to numpy array
        image_array = np.array(image)
        
        # Set image in predictor
        self.predictor.set_image(image_array)
        
        # Generate automatic masks
        masks = self.predictor.generate()
        
        objects = []
        for i, (mask, score) in enumerate(masks):
            if score < 0.8:  # Filter low confidence detections
                continue
            
            # Calculate bounding box
            y_indices, x_indices = np.where(mask)
            if len(y_indices) == 0 or len(x_indices) == 0:
                continue
                
            x1, x2 = np.min(x_indices), np.max(x_indices)
            y1, y2 = np.min(y_indices), np.max(y_indices)
            
            objects.append({
                "id": i,
                "confidence": float(score),
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "area": int(np.sum(mask)),
                "mask": mask.tolist()
            })
        
        return objects
    
    def classify_object(self, image: Image.Image, bbox: List[int]) -> str:
        """Classify the object in the given bounding box"""
        # For now, return a placeholder. This will be replaced with actual classification
        return "unknown_object"
    
    async def process_frame(self, image_data: str) -> Dict[str, Any]:
        """Process a frame from the camera"""
        try:
            # Process image
            image = self.process_image(image_data)
            
            # Detect objects
            objects = self.detect_objects(image)
            
            # Classify each object
            for obj in objects:
                obj["class"] = self.classify_object(image, obj["bbox"])
            
            return {
                "success": True,
                "objects": objects
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }