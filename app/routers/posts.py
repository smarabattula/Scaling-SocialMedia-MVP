# Write Data
from fastapi import status, HTTPException, Depends, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, oauth2
import psycopg2

router = APIRouter(prefix = "/posts", tags = ["posts"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostBase)
async def create_post(post: schemas.PostCreate,
                      db: Session = Depends(get_db),
                      user_id: int = Depends(oauth2.get_current_user)):
    try:
        # serializing data
        new_post = models.Post(**post.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while inserting into the database: {e}")

# Read all posts
@router.get("/", response_model= List[schemas.Post])
async def get_posts(db: Session = Depends(get_db)):
    try:
        posts = db.query(models.Post).all()
        return posts
    except psycopg2.Error as e:
        return {"Message": f"An error occurred while querying the database: {e}"}

# Read post with ID (as Path Parameter)
@router.get("/{id}", response_model= schemas.Post)
async def get_post(id: str, db: Session = Depends(get_db)):
    try:
        query = db.query(models.Post).filter(models.Post.id == id)
        result = query.first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
        return result
    except psycopg2.Error as e:
        return {"Message": f"An error occurred while querying the database: {e}"}

# Delete Post with ID
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: str, db: Session = Depends(get_db)):
    query = db.query(models.Post).filter(models.Post.id == id)
    if not query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    query.delete(synchronize_session=False)
    db.commit()
    return {f"Message": f"Post with id {id} successfully deleted!"}

# Update Post
@router.put("/{id}")
async def update_post(id: str, post: schemas.PostBase, db: Session = Depends(get_db)):
    query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = query.first()
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")

    update_data = post.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key != "id":
            setattr(existing_post, key, value)

    db.commit()
    db.refresh(existing_post)
    return existing_post
