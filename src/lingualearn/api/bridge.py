from typing import Dict, Any, Optional
import asyncio
from fastapi import FastAPI, WebSocket, HTTPException
from ..object_learning import EnhancedObjectLearner
from ..voice_input import VoiceInput
from ..sam_integration import SAMObjectDetector
from ..knowledge_base import KnowledgeBase

class LinguaLearnAPI:
    def __init__(self):
        self.app = FastAPI()
        self.kb = KnowledgeBase()
        self.object_learner = EnhancedObjectLearner(self.kb)
        self.voice_input = VoiceInput()
        self.sam = SAMObjectDetector()
        
        self._setup_routes()
        self._active_sessions = {}

    def _setup_routes(self):
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            session_id = str(len(self._active_sessions) + 1)
            self._active_sessions[session_id] = websocket
            
            try:
                while True:
                    message = await websocket.receive_json()
                    response = await self._handle_message(message)
                    await websocket.send_json(response)
            except Exception as e:
                print(f"WebSocket error: {e}")
            finally:
                if session_id in self._active_sessions:
                    del self._active_sessions[session_id]

        @self.app.post("/detect-object")
        async def detect_object(data: Dict[str, Any]):
            try:
                point = data.get('point')
                frame_data = data.get('frame')
                language = data.get('language', 'en')
                
                if not point or not frame_data:
                    raise HTTPException(status_code=400, detail="Missing required data")
                
                # Process frame data and detect object
                result = await self.object_learner.learn_from_image(
                    frame_data,
                    point,
                    language
                )
                
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/record-term")
        async def record_term(data: Dict[str, Any]):
            try:
                language = data.get('language', 'en')
                duration = data.get('duration', 5)
                
                # Record and transcribe audio
                result = await self.voice_input.record_and_transcribe(
                    language=language,
                    duration=duration
                )
                
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/save-term")
        async def save_term(data: Dict[str, Any]):
            try:
                # Extract term data
                object_data = data.get('object')
                term = data.get('term')
                language = data.get('language')
                region = data.get('region')
                added_by = data.get('added_by')
                
                if not all([object_data, term, language]):
                    raise HTTPException(status_code=400, detail="Missing required data")
                
                # Create enhanced term object
                term_obj = EnhancedObjectTerm(
                    object_name=object_data['name'],
                    local_term=term,
                    language=language,
                    region=region,
                    visual_attributes=object_data.get('attributes'),
                    segmentation_mask=object_data.get('mask'),
                    added_by=added_by
                )
                
                # Save to knowledge base
                await self.kb.add_translation(term_obj)
                
                return {
                    'success': True,
                    'term': term_obj
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/terms/{language}")
        async def get_terms(language: str):
            try:
                terms = await self.kb.get_terms_by_language(language)
                return terms
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    async def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming WebSocket messages"""
        action = message.get('action')
        data = message.get('data', {})
        
        if action == 'detect_object':
            return await self.object_learner.learn_from_image(
                data['frame'],
                data['point'],
                data['language']
            )
        elif action == 'record_term':
            return await self.voice_input.record_and_transcribe(
                data['language']
            )
        elif action == 'save_term':
            term_obj = EnhancedObjectTerm(**data)
            await self.kb.add_translation(term_obj)
            return {'success': True, 'term': term_obj}
        else:
            return {'error': 'Unknown action'}

    def run(self, host: str = '0.0.0.0', port: int = 8000):
        """Run the API server"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)