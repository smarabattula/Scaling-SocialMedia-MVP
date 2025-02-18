from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from ..database import get_db
from sqlalchemy.orm import Session, subqueryload
from typing import List, Optional
from .. import models, schemas, oauth2

router = APIRouter(prefix = "/posts", tags = ["posts"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post: schemas.PostCreate,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        # serializing data
        new_post = models.Post(owner_id = current_user.id, **post.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while inserting into the database: {e}")

# Read all posts
@router.get("/", response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db),
                    current_user: models.User = Depends(oauth2.get_current_user),
                    limit: int = 5,
                    sortBy: str = "createdAt",
                    sortAsc: bool = True,
                    search: Optional[str] = ""):
    try:
        # Handling query parameters
        order = models.Post.__table__.c[sortBy].asc() if sortAsc else models.Post.__table__.c[sortBy].desc()
        posts = db.query(models.Post, func.count(models.Likes.post_id).label("likes"))\
            .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
            .options(subqueryload(models.Post.owner))\
            .group_by(models.Post.id)\
            .filter(models.Post.title.contains(search))\
            .order_by(order)\
            .limit(limit).all()

        response = [{"post": post.__dict__, "likes": likes} for post, likes in posts]

        return response
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

# Read post with ID (as Path Parameter)
@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: str,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        post = db.query(models.Post, func.count(models.Likes.post_id).label("likes"))\
            .join(models.Likes, models.Likes.post_id == models.Post.id, isouter=True)\
            .options(subqueryload(models.Post.owner))\
            .group_by(models.Post.id)\
            .filter(models.Post.id == id)\

        result = post.first()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
        post, likes = result
        return {"post": post.__dict__, "likes": likes}
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

# Delete Post with ID
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: str,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):

    query = db.query(models.Post).filter(models.Post.id == id)
    post = query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    query.delete(synchronize_session=False)
    db.commit()
    return {f"Message": f"Post with id {id} successfully deleted!"}

# Update Post
@router.put("/{id}")
async def update_post(id: str,
                      post: schemas.PostBase,
                      db: Session = Depends(get_db),
                      current_user: models.User = Depends(oauth2.get_current_user)):
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

    db.commit()
    db.refresh(existing_post)
    return existing_post
