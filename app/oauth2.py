import jwt
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from jwt import PyJWTError
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from . import schemas
from . import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
# Get the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load the .env file from the parent directory
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)

ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv('ACCESS_TOKEN_EXPIRE_SECONDS'))
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Create JWT Token
async def create_access_token(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode.update({"exp": expiration_time})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify JWT Token Authenticity
async def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

        # Payload data has "user_id"
        id: str = payload.get("user_id")
        if not id:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)
    except PyJWTError:
        raise credentials_exception

    return token_data

async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db)):

    token_data = await verify_access_token(token)
    query = db.query(models.User).filter(models.User.id == token_data.id)
    user = query.first()
    return user
