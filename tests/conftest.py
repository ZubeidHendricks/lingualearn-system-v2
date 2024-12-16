import pytest
import asyncio
from lingualearn.translation import TranslationCore, TranslationConfig


@pytest.fixture
def translation_config():
    return TranslationConfig(
        preserve_expression=True,
        enable_streaming=True,
        offline_fallback=True,
        buffer_size=2048,
        max_latency=100,
    )


@pytest.fixture
def translation_core(translation_config):
    return TranslationCore(translation_config)


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
