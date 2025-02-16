
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from .. import utils
router = APIRouter(prefix="/users", tags = ["users"])

@router.post("/", status_code = status.HTTP_201_CREATED, response_model=schemas.UserGet)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # password hashing
    user.password = utils.hash(user.password)

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/', response_model=List[schemas.UserGet])
async def get_users(db: Session = Depends(get_db)):
    try:
        query = db.query(models.User)
        users = query.all()
        return users
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)


@router.get('/{id}', response_model=schemas.UserGet)
async def get_user(id: int, db: Session = Depends(get_db)):
    query = db.query(models.User).filter(models.User.id == id)
    user = query.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} not available!")
    return user
