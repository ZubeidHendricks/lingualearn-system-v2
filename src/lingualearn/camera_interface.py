import cv2
import asyncio
import numpy as np
from typing import Optional, Callable, Dict
from dataclasses import dataclass
from .object_learning import ObjectLearner, ObjectTerm

@dataclass
class CameraConfig:
    width: int = 1280
    height: int = 720
    fps: int = 30
    auto_focus: bool = True

class CameraInterface:
    def __init__(self, 
                 object_learner: ObjectLearner,
                 config: Optional[CameraConfig] = None):
        self.learner = object_learner
        self.config = config or CameraConfig()
        self.camera = None
        self.is_running = False
        self._current_frame = None
        self._frame_ready = asyncio.Event()

    async def start(self):
        """Start the camera interface"""
        if self.camera is not None:
            return

        self.camera = cv2.VideoCapture(0)  # Use default camera
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        self.camera.set(cv2.CAP_PROP_FPS, self.config.fps)
        
        if self.config.auto_focus:
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera")

        self.is_running = True
        asyncio.create_task(self._capture_frames())

    async def stop(self):
        """Stop the camera interface"""
        self.is_running = False
        if self.camera is not None:
            self.camera.release()
            self.camera = None

    async def _capture_frames(self):
        """Continuously capture frames from camera"""
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                self._current_frame = frame
                self._frame_ready.set()
            await asyncio.sleep(1/self.config.fps)

    async def capture_object(self, 
                           language: str,
                           on_detection: Optional[Callable[[Dict], None]] = None
                           ) -> Optional[Dict]:
        """Capture and identify object in frame"""
        if not self.is_running:
            raise RuntimeError("Camera not started")

        # Wait for next frame
        await self._frame_ready.wait()
        self._frame_ready.clear()

        if self._current_frame is None:
            return None

        # Get object terms for the frame
        terms = await self.learner.identify_object(
            self._current_frame,
            language
        )

        result = {
            'frame': self._current_frame,
            'terms': terms
        }

        if on_detection:
            on_detection(result)

        return result

    async def learn_new_term(self,
                           term: ObjectTerm,
                           on_learned: Optional[Callable[[Dict], None]] = None
                           ) -> Optional[Dict]:
        """Learn a new term for captured object"""
        if not self.is_running:
            raise RuntimeError("Camera not started")

        # Wait for next frame
        await self._frame_ready.wait()
        self._frame_ready.clear()

        if self._current_frame is None:
            return None

        # Learn the new term
        result = await self.learner.learn_object_term(
            self._current_frame,
            term
        )

        if on_learned:
            on_learned(result)

        return result

    def get_preview_frame(self) -> Optional[np.ndarray]:
        """Get the current camera frame for preview"""
        return self._current_frame

    async def toggle_flash(self, on: bool):
        """Toggle camera flash/torch if available"""
        if self.camera is not None:
            try:
                self.camera.set(cv2.CAP_PROP_FLASH, int(on))
            except:
                pass  # Flash might not be available

    async def toggle_autofocus(self, on: bool):
        """Toggle camera autofocus"""
        if self.camera is not None:
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, int(on))
            self.config.auto_focus = on