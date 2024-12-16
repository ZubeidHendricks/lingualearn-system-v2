import pytest
import asyncio
from lingualearn.translation import TranslationMode, TranslationCore, TranslationConfig


@pytest.mark.asyncio
async def test_translation_initialization(translation_core):
    assert translation_core is not None
    assert translation_core.config is not None
    assert translation_core.config.preserve_expression is True
    assert translation_core.config.enable_streaming is True


@pytest.mark.asyncio
async def test_translation_modes():
    assert TranslationMode.SPEECH_TO_SPEECH.value == "S2ST"
    assert TranslationMode.SPEECH_TO_TEXT.value == "S2TT"
    assert TranslationMode.TEXT_TO_SPEECH.value == "T2ST"
    assert TranslationMode.TEXT_TO_TEXT.value == "T2TT"


@pytest.mark.asyncio
async def test_custom_translation_config():
    config = TranslationConfig(
        preserve_expression=False,
        enable_streaming=False,
        offline_fallback=True,
        buffer_size=4096,
        max_latency=200,
    )
    core = TranslationCore(config)
    assert core.config.preserve_expression is False
    assert core.config.enable_streaming is False
    assert core.config.buffer_size == 4096
    assert core.config.max_latency == 200


@pytest.mark.asyncio
async def test_logger_initialization(translation_core):
    assert translation_core.logger is not None


@pytest.fixture
def mock_audio_data():
    return b"dummy_audio_data"


@pytest.fixture
def mock_text_data():
    return "Hello, world!"


@pytest.mark.asyncio
async def test_translation_with_invalid_mode(translation_core, mock_audio_data):
    with pytest.raises(ValueError):
        await translation_core.translate(
            content=mock_audio_data,
            source_lang="en",
            target_lang="xho",
            mode="INVALID_MODE",
        )


@pytest.mark.asyncio
async def test_offline_fallback(translation_core, mock_audio_data):
    # Simulate main translation failure
    translation_core._translate_batch = asyncio.coroutine(
        lambda *args, **kwargs: raise_(Exception("Translation failed"))
    )

    result = await translation_core.translate(
        content=mock_audio_data,
        source_lang="en",
        target_lang="xho",
        mode=TranslationMode.SPEECH_TO_SPEECH,
    )

    assert result["status"] == "success_offline"


def raise_(ex):
    raise ex
