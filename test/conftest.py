import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from app import app

@pytest.fixture(scope="module")
def client(mock_db_pool, mock_redis):
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def mock_db_pool():
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    
    # Mock data for tests
    mock_post_row = {
        "id": 1,
        "title": "Test Post",
        "content": "This is a test post.",
        "created_at": datetime.now()
    }
    
    mock_comment_row = {
        "id": 1,
        "content": "This is a test comment.",
        "created_at": datetime.now(),
        "post_id": 1
    }
    
    # Create a side effect function to return different data based on the query
    def fetchrow_side_effect(*args, **kwargs):
        # If it's a comment insert query, return comment data
        if args and "INSERT INTO comments" in args[0]:
            return mock_comment_row
        # Otherwise return post data
        return mock_post_row
    
    # Configure mock responses
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.fetchrow = AsyncMock(side_effect=fetchrow_side_effect)
    mock_conn.fetchval = AsyncMock(return_value=True)
    mock_conn.execute = AsyncMock()
    
    # Create a proper async context manager
    class MockAcquire:
        def __init__(self, conn):
            self.conn = conn
            
        async def __aenter__(self):
            return self.conn
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None
    
    mock_pool.acquire = MagicMock(return_value=MockAcquire(mock_conn))
    
    with patch("app.db_pool", mock_pool):
        yield mock_pool

@pytest.fixture(scope="module", autouse=True)
def mock_redis():
    mock_redis = MagicMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.setex = AsyncMock()
    mock_redis.keys = AsyncMock(return_value=[])
    mock_redis.delete = AsyncMock()
    with patch("app.redis", mock_redis):
        yield mock_redis 