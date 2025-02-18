from fastapi import FastAPI
from . import models
from .schemas import *
from .database import engine
from .routers import posts, users, auth, likes

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Link routers for all paths
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(likes.router)

# Path
@app.get("/")
async def read_root():
    return {"Hello": "World"}
