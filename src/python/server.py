import asyncio
import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import base64
import torch
from segment_anything import sam_model_registry, SamPredictor

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SAM
SAM_CHECKPOINT = "models/sam_vit_h_4b8939.pth"
MODEL_TYPE = "vit_h"

class ObjectDetector:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        self.sam = sam_model_registry[MODEL_TYPE](checkpoint=SAM_CHECKPOINT)
        self.sam.to(device=self.device)
        self.predictor = SamPredictor(self.sam)

    async def detect_objects(self, image_data: str):
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Set image in predictor
            self.predictor.set_image(image_array)
            
            # Generate automatic masks
            masks = self.predictor.generate()
            
            # Process results
            objects = []
            for i, (mask, score) in enumerate(zip(masks, scores)):
                if score < 0.8:  # Filter low confidence detections
                    continue
                    
                objects.append({
                    "id": i,
                    "confidence": float(score),
                    "bbox": get_bbox(mask),
                    "area": int(mask.sum())
                })
            
            return {
                "success": True,
                "objects": objects
            }
            
        except Exception as e:
            logging.error(f"Detection error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Initialize detector
detector = ObjectDetector()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "detect":
                result = await detector.detect_objects(data["image"])
                await websocket.send_json(result)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)