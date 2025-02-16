from typing import Optional
from fastapi import FastAPI,Response, status, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from . import db_connect
import psycopg2
import random

BASE62_ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def generate_base62_id(length=6):
    return ''.join(random.choices(BASE62_ALPHABET, k=length))

# Pydantic Model
class Post(BaseModel):
    id: int = None
    title: str
    content: str
    published: bool = True
    createdAt: datetime = None

class PostUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
    createdAt: Optional[datetime] = None

conn = db_connect.open_connection()

app = FastAPI()

# Path
@app.get("/")
async def read_root():
    return {"Hello": "World"}

# First Matching Path Operation is processed!
# All other matching paths won't be processed
@app.get("/")
async def read_root():
    return {"Hello": "Fron the other side"}

# Write Data
@app.post("/createpost", status_code= status.HTTP_201_CREATED)
async def create_post(post: Post):

    try:
        post_dict = post.model_dump()
        current_id = generate_base62_id()
        post_dict["id"] = current_id
        query = f'INSERT INTO "fastapi-db".posts VALUES (%s, %s, %s, %s) RETURNING *'
        # Default value for published handled by Pydantic Model
        data = (post_dict["id"], post_dict["title"],post_dict["content"], post_dict["published"])
        if db_connect.insert_update_post(conn, query, data):
            return {"Message": f"Post with id {post_dict["id"]} successfully created"}
        else:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while inserting into the database")
    except psycopg2.Error as e:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while inserting into the database")

# Read all posts
@app.get("/posts")
async def get_posts():
    try:
        query = 'SELECT * FROM "fastapi-db".posts'
        results = db_connect.query_posts(conn, query, None)
        return results
    except psycopg2.Error as e:
        print()
        return {"Message" : f"An error occurred while querying the database: {e}"}

# Read post with ID (as Path Parameter)
@app.get("/posts/{id}")
async def get_post(id: str, response: Response):
    query = f'SELECT * FROM "fastapi-db".posts WHERE ID = %s LIMIT 1'
    data = (id, )
    result = db_connect.query_posts(conn, query, data)
    if not result:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f"post with id {id} not found"}
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id {id} not found")

    return result

# Delete Post with ID
@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
async def delete_post(id):
    query = f'SELECT DISTINCT ID FROM "fastapi-db".posts WHERE ID = %s LIMIT 1'
    data = (id,)
    search = db_connect.query_posts(conn, query, data)
    if not search:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    query = f'DELETE FROM "fastapi-db".posts WHERE ID = %s RETURNING *'
    if not db_connect.delete_post(conn, query, data):
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    return {f"Message": f"Post with id {id} successfully deleted!"}

# Update Post
@app.put("/posts/{id}")
async def update_post(id: str, post: Post):
    query = f'SELECT DISTINCT ID FROM "fastapi-db".posts WHERE ID = %s LIMIT 1'
    data = (id,)
    search = db_connect.query_posts(conn, query, data)
    if not search:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    # Update query slightly different compared to T-SQL
    query = f"""UPDATE "fastapi-db".posts SET title = %s, content = %s, published = %s, "createdAt" = %s WHERE ID = %s"""
    data = (post.title, post.content, post.published, post.createdAt, post.id)
    updated_result = db_connect.insert_update_post(conn, query, data)
    if not updated_result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND)

    return {"message": f"post with id {id} successfully updated!"}
