from fastapi import FastAPI,HTTPException,File,UploadFile, Form, Depends
from app.schemas import PostCreate,PostResponse
from app.db import Post,create_db_and_tables,get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy.future import select
from app.images import imagekit
import os 

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield

app=FastAPI(lifespan=lifespan)



@app.post("/upload")
async def upload_file(file:UploadFile=File(...),
                      caption:str=Form(""),
                      session: AsyncSession=Depends(get_async_session)):
    try:
        file_bytes = await file.read()

        upload_result = imagekit.files.upload(
            file=file_bytes,
            file_name=file.filename,
            use_unique_file_name=True,
            folder="backend-upload",
        )

        post = Post(
            caption=caption,
            file_id=upload_result.file_id,
            url=upload_result.url,
            file_type="video" if (file.content_type or "").startswith("video") else "image",
            file_name=file.filename,
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()

@app.get("/feed")
async def get_feed(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts=[row[0] for row in result.all()]

    posts_data=[]

    for post in posts:
        posts_data.append({
            "id":str(post.id),
            "caption":post.caption,
            "url":post.url,
            "file_type":post.file_type,
            "file_name":post.file_name,
            "created_at":post.created_at.isoformat()
        })
    return posts_data

@app.delete("/delete/{post_id}")
async def delete_post(post_id:str,session:AsyncSession=Depends(get_async_session)): 
    
    result=await session.execute(select(Post).where(Post.id==post_id))
    post=result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404,detail="Post not found")

    try:
        imagekit.files.delete(file_id=post.file_id)
        
        await session.delete(post)
        await session.commit()
        return {"message":"Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
