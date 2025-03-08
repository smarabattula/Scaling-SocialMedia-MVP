import pytest
from ..server_ORM import app
from fastapi.testclient import TestClient
from fastapi import Depends
from ..database import get_db
from sqlalchemy.orm import Session

def get_test_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)
def test_something():
    response = client.get("/posts")
    assert response.status_code == 401
    assert response.json() == {"Hello": "World"}

