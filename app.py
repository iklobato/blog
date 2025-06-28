import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

import aioredis
import asyncpg
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class Comment(BaseModel):
    id: Optional[int] = None
    content: str = Field(..., min_length=1, max_length=1000)
    created_at: Optional[datetime] = None
    post_id: Optional[int] = None


class BlogPost(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    created_at: Optional[datetime] = None
    comments: Optional[List[Comment]] = []
    comment_count: Optional[int] = None


db_pool = None
redis = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, redis

    db_pool = await asyncpg.create_pool(os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/blog_db"))
    redis = await aioredis.create_redis_pool(os.getenv("REDIS_URL", "redis://localhost:6379"), encoding="utf-8")

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blog_posts (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                content VARCHAR(1000) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                post_id INTEGER REFERENCES blog_posts(id) ON DELETE CASCADE
            )
        """
        )

    yield

    await db_pool.close()
    await redis.close()


app = FastAPI(title="Blog API", lifespan=lifespan)


async def get_cache(key: str):
    try:
        data = await redis.get(key)
        return json.loads(data) if data else None
    except:
        return None


async def set_cache(key: str, data, ttl: int = 300):
    try:
        await redis.setex(key, ttl, json.dumps(data, default=str))
    except:
        pass


async def clear_cache(pattern: str):
    try:
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
    except:
        pass


@app.get("/api/posts", response_model=List[BlogPost])
async def get_posts():
    cached = await get_cache("posts")
    if cached:
        return [BlogPost(**post) for post in cached]

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT p.id, p.title, p.created_at, COUNT(c.id) as comment_count
            FROM blog_posts p
            LEFT JOIN comments c ON p.id = c.post_id
            GROUP BY p.id, p.title, p.created_at
            ORDER BY p.created_at DESC
        """
        )

        posts = [{"id": r["id"], "title": r["title"], "created_at": r["created_at"], "comment_count": r["comment_count"]} for r in rows]

        await set_cache("posts", posts)
        return [BlogPost(**post) for post in posts]


@app.post("/api/posts", response_model=BlogPost, status_code=201)
async def create_post(post: BlogPost):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO blog_posts (title, content) 
            VALUES ($1, $2) 
            RETURNING id, title, content, created_at
        """,
            post.title,
            post.content,
        )

        await clear_cache("posts")

        return BlogPost(id=row["id"], title=row["title"], content=row["content"], created_at=row["created_at"], comments=[])


@app.get("/api/posts/{post_id}", response_model=BlogPost)
async def get_post(post_id: int):
    cache_key = f"post:{post_id}"
    cached = await get_cache(cache_key)
    if cached:
        comments = [Comment(**c) for c in cached["comments"]]
        cached["comments"] = comments
        return BlogPost(**cached)

    async with db_pool.acquire() as conn:
        post_row = await conn.fetchrow(
            """
            SELECT id, title, content, created_at FROM blog_posts WHERE id = $1
        """,
            post_id,
        )

        if not post_row:
            raise HTTPException(status_code=404, detail="Post not found")

        comment_rows = await conn.fetch(
            """
            SELECT id, content, created_at, post_id
            FROM comments WHERE post_id = $1 ORDER BY created_at ASC
        """,
            post_id,
        )

        comments = [Comment(id=r["id"], content=r["content"], created_at=r["created_at"], post_id=r["post_id"]) for r in comment_rows]

        post = BlogPost(
            id=post_row["id"], title=post_row["title"], content=post_row["content"], created_at=post_row["created_at"], comments=comments
        )

        await set_cache(cache_key, post.model_dump())
        return post


@app.post("/api/posts/{post_id}/comments", response_model=Comment, status_code=201)
async def add_comment(post_id: int, comment: Comment):
    async with db_pool.acquire() as conn:
        post_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM blog_posts WHERE id = $1)", post_id)
        if not post_exists:
            raise HTTPException(status_code=404, detail="Post not found")

        row = await conn.fetchrow(
            """
            INSERT INTO comments (content, post_id) 
            VALUES ($1, $2) 
            RETURNING id, content, created_at, post_id
        """,
            comment.content,
            post_id,
        )

        await clear_cache("posts")
        await clear_cache(f"post:{post_id}")

        return Comment(id=row["id"], content=row["content"], created_at=row["created_at"], post_id=row["post_id"])


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now()}


@app.get("/")
async def root():
    return {"message": "Blog API", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
