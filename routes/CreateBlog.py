from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.responses import JSONResponse
from routes.crud import get_current_user
from models.schemas import CreateBlog, UpdateBlog
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from models.sqlDATA import Blog, User
from sqlalchemy import select
from sqlalchemy.future import select
from starlette.config import Config

createBlog = APIRouter()

@createBlog.post("/auth/create_blog", status_code=status.HTTP_201_CREATED)
async def UserCreateBlog(
        create_blog: CreateBlog,
        db: AsyncSession = Depends(get_db),
        authorization: str = Header(None),
        current_user:User = Depends(get_current_user)):  
    
    if not authorization:
        raise HTTPException(status_code=404, detail="Missing Authorization header")
    
    new_blog = Blog(
        owner_id=current_user.id,
        author=current_user.username,  # Assign the logged-in user's username as the author
        title = create_blog.title,
        body = create_blog.body, 
    )
    db.add(new_blog)
    await db.commit()
    await db.refresh(new_blog)    
    return new_blog


@createBlog.get("/auth/blogs", response_model=List[CreateBlog])
async def get_blogs(db: AsyncSession = Depends(get_db)):
    blogs = await db.execute(select(Blog))
    users_blog = blogs.scalars().all()
    return users_blog



@createBlog.get("/auth/blogs/{id}", response_model=CreateBlog)
async def get_blog(id: int, db: AsyncSession = Depends(get_db)):
    query = select(Blog).where(Blog.id == id)
    result = await db.execute(query)
    blog = result.scalar_one_or_none()  # Extract the first result or None

    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    return blog

@createBlog.delete("/auth/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
        id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(Blog).filter(Blog.id == id, Blog.owner_id == current_user.id)
    result = await db.execute(query)
    blog = result.scalar_one_or_none()
    
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found or not authorized to delete")
    
    await db.delete(blog)
    await db.commit()
    
    return {"detail": "Blog deleted successfully"}


@createBlog.put("/auth/update/{id}")
async def update_blog(id: int, update_blog: UpdateBlog, db: AsyncSession = Depends(get_db)):
    # Query the blog post by id
    async with db as session:
        result = await session.execute(select(Blog).filter(Blog.id == id))
        blog_to_update = result.scalar_one_or_none()
        
        if not blog_to_update:
            raise HTTPException(status_code=404, detail="Blog not found")
        
        # Update the fields that are provided in the update_blog object
        if update_blog.title:
            blog_to_update.title = update_blog.title
        if update_blog.body:
            blog_to_update.body = update_blog.body

        # Commit the changes
        await session.commit()

        # Return a message to indicate that the blog was successfully updated
        return JSONResponse(content={"message":"updated successfully"}, status_code=status.HTTP_200_OK)