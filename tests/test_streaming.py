import pytest
import asyncio
from lingualearn.streaming import StreamingServer


@pytest.fixture
def streaming_server():
    return StreamingServer()


@pytest.mark.asyncio
async def test_streaming_initialization(streaming_server):
    assert streaming_server is not None
    assert streaming_server.connections == {}
    assert streaming_server.logger is not None


@pytest.mark.asyncio
async def test_create_streaming_session(streaming_server):
    session_config = {
        'source_lang': 'en',
        'target_lang': 'xho',
        'preserve_style': True
    }
    
    session_id = await streaming_server.create_session(session_config)
    assert session_id in streaming_server.connections
    assert streaming_server.connections[session_id]['config'] == session_config


@pytest.mark.asyncio
async def test_close_streaming_session(streaming_server):
    session_config = {
        'source_lang': 'en',
        'target_lang': 'xho',
        'preserve_style': True
    }
    
    session_id = await streaming_server.create_session(session_config)
    await streaming_server.close_session(session_id)
    assert session_id not in streaming_server.connections


@pytest.mark.asyncio
async def test_get_active_streams(streaming_server):
    session1 = await streaming_server.create_session({
        'source_lang': 'en',
        'target_lang': 'xho',
        'preserve_style': True
    })
    
    session2 = await streaming_server.create_session({
        'source_lang': 'en',
        'target_lang': 'zul',
        'preserve_style': True
    })
    
    active_streams = streaming_server.get_active_streams()
    assert len(active_streams) == 2
    assert session1 in active_streams
    assert session2 in active_streams
