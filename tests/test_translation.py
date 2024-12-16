import pytest
import asyncio
from lingualearn.translation import TranslationMode

@pytest.mark.asyncio
async def test_translation_initialization(translation_core):
    assert translation_core is not None
    assert translation_core.config is not None

@pytest.mark.asyncio
async def test_translation_modes():
    assert TranslationMode.SPEECH_TO_SPEECH.value == "S2ST"
    assert TranslationMode.SPEECH_TO_TEXT.value == "S2TT"
    assert TranslationMode.TEXT_TO_SPEECH.value == "T2ST"
    assert TranslationMode.TEXT_TO_TEXT.value == "T2TT"