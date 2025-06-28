import pytest
from fastapi.testclient import TestClient
from app import app
import anyio

@pytest.fixture(scope="module")
def client(mock_db_pool, mock_redis):
    return TestClient(app)

class TestBlogAPI:
    @pytest.mark.anyio
    async def test_get_posts(self, client):
        response = client.get("/api/posts")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.anyio
    async def test_create_post(self, client):
        new_post = {"title": "Test Post", "content": "This is a test post."}
        response = client.post("/api/posts", json=new_post)
        assert response.status_code == 201
        assert response.json()["title"] == new_post["title"]

    @pytest.mark.anyio
    async def test_get_post(self, client):
        response = client.get("/api/posts/1")
        assert response.status_code == 200
        assert "title" in response.json()

    @pytest.mark.anyio
    async def test_add_comment(self, client):
        new_comment = {"content": "This is a test comment."}
        response = client.post("/api/posts/1/comments", json=new_comment)
        assert response.status_code == 201
        assert response.json()["content"] == new_comment["content"]

    @pytest.mark.anyio
    async def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok" 