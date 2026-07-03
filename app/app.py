from fastapi import FastAPI,HTTPException
from app.schemas import PostCreate,PostResponse
from app.db import Post,create_db_and_tables,get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield

app=FastAPI(lifespan=lifespan)


text_posts={}

@app.get("/posts")
def get_all_posts(limit:int):
    if limit is not None:
        return text_posts[:limit]
    return text_posts

@app.get("/posts/{id}")
def get_post(id:int)->PostResponse:
    if id not in text_posts: raise HTTPException(status_code=404,detail="Post not found")

    return text_posts.get(id)

@app.post("/posts")
def create_post(post:PostCreate)->PostResponse:
    id=len(text_posts)+1
    new_post={"title":post.title,"content":post.content}

    text_posts[id]=new_post

    return new_post
