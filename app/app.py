from fastapi import FastAPI,HTTPException,File,UploadFile, Form, Depends
from app.schemas import PostCreate,PostResponse
from app.db import Post, User, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy.future import select
from app.images import imagekit
import os 
from app.users import auth_backend,fastapi_users,current_active_user
from app.schemas import UserRead,UserCreate,UserUpdate

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield

app=FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead,UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)   
app.include_router(
    fastapi_users.get_verify_router(UserRead),  
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead,UserUpdate),    
    prefix="/users",
    tags=["users"],
)

@app.post("/upload")
async def upload_file(file:UploadFile=File(...),
                      caption:str=Form(""),
                      user:UserRead=Depends(current_active_user),
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
            user_id=user.id,
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
async def get_feed(session: AsyncSession = Depends(get_async_session),user:UserRead=Depends(current_active_user)):
    result = await session.execute(
        select(Post, User.email)
        .outerjoin(User, Post.user_id == User.id)
        .order_by(Post.created_at.desc())
    )
    rows = result.all()

    posts_data=[]

    for post, email in rows:
        posts_data.append({
            "id":str(post.id),
            "user_id":str(post.user_id),
            "caption":post.caption,
            "url":post.url,
            "file_type":post.file_type,
            "file_name":post.file_name,
            "created_at":post.created_at.isoformat(),
            "is_owner":post.user_id==user.id,
            "email":email or "Unknown" 
        })
    return posts_data

@app.delete("/delete/{post_id}")
async def delete_post(post_id:str,session:AsyncSession=Depends(get_async_session),user:UserRead=Depends(current_active_user)): 
    
    result=await session.execute(select(Post).where(Post.id==post_id))
    post=result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404,detail="Post not found")
    
    if post.user_id != user.id:
        raise HTTPException(status_code=403,detail="You are not authorized to delete this post")

    try:
        imagekit.files.delete(file_id=post.file_id)
        
        await session.delete(post)
        await session.commit()
        return {"message":"Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
