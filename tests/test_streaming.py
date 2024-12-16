import pytest
from lingualearn.streaming import StreamingServer

@pytest.fixture
def streaming_server():
    return StreamingServer()

@pytest.mark.asyncio
async def test_streaming_initialization(streaming_server):
    assert streaming_server is not None
    assert streaming_server.connections == {}