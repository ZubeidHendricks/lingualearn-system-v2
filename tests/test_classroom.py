import pytest
from lingualearn.classroom import ClassroomManager

@pytest.fixture
def classroom_manager():
    return ClassroomManager()

@pytest.mark.asyncio
async def test_classroom_initialization(classroom_manager):
    assert classroom_manager is not None
    assert classroom_manager.active_sessions == {}