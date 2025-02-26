from fastapi import status, HTTPException, Depends, APIRouter
from redis.commands.json.path import Path

from ..redis_cache import redis_session, update_like_count
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2

router = APIRouter(
    prefix = "/like",
    tags = ["Vote"]
    )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(vote: schemas.Like,
         db: Session = Depends(get_db),
         current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post id {vote.post_id} doesn't exist")

    vote_query = db.query(models.Likes).filter(models.Likes.post_id == vote.post_id, models.Likes.user_id == current_user.id)
    vote_result = vote_query.first()
    if vote_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User id {current_user.id} already liked post id {vote.post_id}")
    else:
        try:
            new_like = models.Likes(post_id = vote.post_id, user_id = current_user.id)
            db.add(new_like)
            db.commit()
            await update_like_count(vote.post_id, True)
            return {"Message": f"User id {current_user.id} liked Post id {vote.post_id} successfully!"}
        except Exception as e:
            return {"Message": f'{str(e).replace('\n', '')}'}

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def unvote(vote: schemas.Like,
         db: Session = Depends(get_db),
         current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post id {vote.post_id} doesn't exist")

    vote_query = db.query(models.Likes).filter(models.Likes.post_id == vote.post_id, models.Likes.user_id == current_user.id)
    vote_result = vote_query.first()
    if not vote_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User id {current_user.id} hasn't liked post id {vote.post_id} or post doesn't exist")
    else:
        vote_query.delete(synchronize_session=False)
        db.commit()
        await update_like_count(vote.post_id, False)
        return {f"Message": f"User id {current_user.id} disliked Post id {vote.post_id} successfully!"}
