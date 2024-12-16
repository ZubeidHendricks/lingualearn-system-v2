from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import asyncio
import logging
from enum import Enum

class TranslationMode(Enum):
    SPEECH_TO_SPEECH = "S2ST"
    SPEECH_TO_TEXT = "S2TT"
    TEXT_TO_SPEECH = "T2ST"
    TEXT_TO_TEXT = "T2TT"

@dataclass
class TranslationConfig:
    preserve_expression: bool = True
    enable_streaming: bool = True
    offline_fallback: bool = True
    buffer_size: int = 2048
    max_latency: int = 100  # milliseconds

class TranslationCore:
    """Core translation system implementation"""
    
    def __init__(self, config: TranslationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)