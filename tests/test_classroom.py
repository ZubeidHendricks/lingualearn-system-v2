import pytest
from uuid import UUID
from lingualearn.classroom import ClassroomManager


@pytest.fixture
def classroom_manager():
    return ClassroomManager()


@pytest.mark.asyncio
async def test_classroom_initialization(classroom_manager):
    assert classroom_manager is not None
    assert classroom_manager.active_sessions == {}
    assert classroom_manager.logger is not None


@pytest.mark.asyncio
async def test_create_session(classroom_manager):
    session_id = await classroom_manager.create_session(
        {
            "teacher_id": "teacher123",
            "class_name": "Grade 10 Science",
            "target_languages": ["xho", "zul", "sot"],
        }
    )

    assert isinstance(session_id, str)
    try:
        uuid_obj = UUID(session_id)
        assert uuid_obj is not None
    except ValueError:
        pytest.fail("Session ID is not a valid UUID")

    assert session_id in classroom_manager.active_sessions
    assert classroom_manager.active_sessions[session_id]["teacher_id"] == "teacher123"


@pytest.mark.asyncio
async def test_end_session(classroom_manager):
    session_id = await classroom_manager.create_session(
        {
            "teacher_id": "teacher123",
            "class_name": "Grade 10 Science",
            "target_languages": ["xho", "zul", "sot"],
        }
    )

    await classroom_manager.end_session(session_id)
    assert session_id not in classroom_manager.active_sessions


@pytest.mark.asyncio
async def test_get_active_sessions(classroom_manager):
    session1 = await classroom_manager.create_session(
        {
            "teacher_id": "teacher123",
            "class_name": "Grade 10 Science",
            "target_languages": ["xho", "zul"],
        }
    )

    session2 = await classroom_manager.create_session(
        {
            "teacher_id": "teacher456",
            "class_name": "Grade 11 Math",
            "target_languages": ["sot", "nbl"],
        }
    )

    active_sessions = classroom_manager.get_active_sessions()
    assert len(active_sessions) == 2
    assert session1 in active_sessions
    assert session2 in active_sessions
