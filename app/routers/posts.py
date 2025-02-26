from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2
from ..redis_cache import process_post_on_redis, redis_session
from redis.commands.json.path import Path
import asyncio

router = APIRouter(prefix = "/posts", tags = ["posts"])

# Write new post
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut)
async def create_post(post: schemas.PostCreate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
    try:

        async def save_to_db(post, current_user, db):
            new_post = models.Post(owner_id=current_user.id, **post.model_dump())
            db.add(new_post)
            db.commit()
            db.refresh(new_post)
            return new_post

        # Run both tasks concurrently
        save_db_task = asyncio.create_task(save_to_db(post, current_user, db))
        save_redis_task = asyncio.create_task(process_post_on_redis(post, 0, current_user.id))

        results = await asyncio.gather(save_db_task, save_redis_task)
        return results[-1]
    except HTTPException as e:
        db.rollback()
        async with redis_session() as r:
            await r.delete(f"post:{post.id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while inserting into the database: {e}")

# Read all posts, with query parameters
@router.get("", response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db),
                    current_user: models.User = Depends(oauth2.get_current_user),
                    limit: int = 5, sortBy: str = "createdAt", sortAsc: bool = True, search: Optional[str] = ""):
    try:

        # Handling query parameters
        order = models.Post.__table__.c[sortBy].asc() if sortAsc else models.Post.__table__.c[sortBy].desc()
        posts = db.query(models.Post, func.count(models.Likes.post_id).label("likes"))\
            .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
            .group_by(models.Post.id)\
            .filter(models.Post.title.contains(search))\
            .order_by(order)\
            .limit(limit).all()

        response = []

        tasks = [process_post_on_redis(post, likes) for post, likes in posts]
        response = await asyncio.gather(*tasks)
        return response

    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

# Get post by ID
@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: str, db: Session = Depends(get_db),
                   current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        async with redis_session() as r:
            cached_post = r.json().get(f"post:{id}")
            if cached_post:
                print("Read from cache")
                return cached_post  # Return if found

        # Fetch post from DB
        result = db.query(models.Post, func.count(models.Likes.post_id).label("likes"))\
            .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
            .group_by(models.Post.id)\
            .filter(models.Post.id == id)\
            .first()  # Execute query

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

        post, likes = result  # Unpacking the result correctly

        # Save searched data to Redis and return response
        post_out = await process_post_on_redis(post, likes)
        print("Read from db")
        return post_out

    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

# Delete Post with ID
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: str,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        query = db.query(models.Post).filter(models.Post.id == id)
        post = query.first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if post.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        query.delete(synchronize_session=False)

        # Delete from cache if present
        async with redis_session() as r:
            r.delete(f"post:{id}")

        db.commit()
        return {f"Message": f"Post with id {id} successfully deleted!"}

    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"post with id {id} couldn't be deleted with error: {e}")


# Update Post
@router.put("/{id}")
async def update_post(id: str,
                      post: schemas.PostBase,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        query = db.query(models.Post).filter(models.Post.id == id)
        existing_post = query.first()
        if not existing_post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
        elif existing_post.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        update_data = post.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key != "id":
                setattr(existing_post, key, value)

        # Update cache
        async with redis_session() as r:
            cached_post = r.json().get(f"post:{id}")
            likes = cached_post["likes"] if cached_post else 0

        await process_post_on_redis(existing_post, likes)

        db.commit()
        db.refresh(existing_post)
        return existing_post

    except HTTPException as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"post with id {id} couldn't be updated with error: {e}")
