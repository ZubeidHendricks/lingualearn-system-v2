import pytest
import asyncio
from lingualearn.translation import TranslationCore, TranslationConfig


@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
