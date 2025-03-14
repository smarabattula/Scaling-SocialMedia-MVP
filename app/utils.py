from passlib.context import CryptContext
import random
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE62_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def generate_base62_id(length=6):
    return ''.join(random.choices(BASE62_ALPHABET, k=length))

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
