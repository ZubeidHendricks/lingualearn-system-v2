import asyncio
import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from object_detection import ObjectDetector
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize object detector
detector = ObjectDetector()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_json()
            
            # Process message based on type
            if message["type"] == "detect":
                logger.info("Processing detection request")
                result = await detector.process_frame(message["image"])
                await websocket.send_json(result)
                
            elif message["type"] == "ping":
                await websocket.send_json({"type": "pong"})
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)