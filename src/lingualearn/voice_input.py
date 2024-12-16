import torch
import whisper
import asyncio
import sounddevice as sd
import numpy as np
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass

@dataclass
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1
    duration: float = 5.0  # seconds
    device: Optional[str] = None

class VoiceInput:
    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        # Initialize Whisper model for ASR
        self.model = whisper.load_model("base")
        self.recording = False
        self._audio_buffer = []

    async def start_recording(self):
        """Start recording audio"""
        if self.recording:
            return

        self.recording = True
        self._audio_buffer = []

        def callback(indata, frames, time, status):
            if status:
                print(f"Recording error: {status}")
            if self.recording:
                self._audio_buffer.append(indata.copy())

        # Start recording stream
        self.stream = sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            callback=callback,
            dtype=np.float32
        )
        self.stream.start()

    async def stop_recording(self) -> np.ndarray:
        """Stop recording and return audio data"""
        self.recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

        if not self._audio_buffer:
            return np.array([])

        # Combine audio chunks
        audio_data = np.concatenate(self._audio_buffer, axis=0)
        self._audio_buffer = []
        return audio_data

    async def transcribe_audio(self, audio_data: np.ndarray,
                             language: str) -> Dict[str, any]:
        """Transcribe recorded audio using Whisper"""
        # Convert audio to format expected by Whisper
        audio_float32 = audio_data.flatten().astype(np.float32)

        # Transcribe using Whisper
        result = self.model.transcribe(
            audio_float32,
            language=language,
            task='transcribe'
        )

        return {
            'text': result['text'],
            'language': result['language'],
            'segments': result['segments']
        }

    async def record_and_transcribe(self, language: str,
                                  on_transcription: Optional[Callable] = None
                                  ) -> Dict[str, any]:
        """Record audio and transcribe it"""
        # Start recording
        await self.start_recording()
        
        # Record for specified duration
        await asyncio.sleep(self.config.duration)
        
        # Stop recording and get audio data
        audio_data = await self.stop_recording()
        
        if len(audio_data) == 0:
            return {
                'success': False,
                'error': 'No audio recorded'
            }

        # Transcribe the audio
        result = await self.transcribe_audio(audio_data, language)
        
        if on_transcription:
            on_transcription(result)

        return {
            'success': True,
            **result
        }

    def set_audio_device(self, device_name: str) -> bool:
        """Set the audio input device"""
        devices = sd.query_devices()
        for device in devices:
            if device['name'] == device_name and device['max_input_channels'] > 0:
                self.config.device = device_name
                return True
        return False

    def list_audio_devices(self) -> List[Dict]:
        """List available audio input devices"""
        devices = sd.query_devices()
        return [{
            'name': device['name'],
            'channels': device['max_input_channels'],
            'sample_rates': device['default_samplerate']
        } for device in devices if device['max_input_channels'] > 0]