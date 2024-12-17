import asyncio
import logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from object_detection import ObjectDetector
from typing import Dict, Any
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize object detector
detector = ObjectDetector()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        # Send initial connection confirmation
        await websocket.send_json({"type": "connection", "status": "connected"})
        
        while True:
            try:
                # Receive message
                message = await websocket.receive_json()
                logger.info(f"Received message type: {message.get('type')}")
                
                # Process message based on type
                if message["type"] == "detect":
                    logger.info("Processing detection request")
                    result = await detector.process_frame(message["image"])
                    await websocket.send_json(result)
                    
                elif message["type"] == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if not websocket.client_state == websocket.application_state == "disconnected":
            await websocket.close()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, log_level="info", reload=True)