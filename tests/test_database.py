import pytest
from sqlalchemy import text

def test_database_connection(test_session):
    result = test_session.execute(text("SELECT 1"))
    assert result.scalar() == 1