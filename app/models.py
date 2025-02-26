from .database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship

# SQLAlchemy Models
# Used for defining columns on tables
# And simplify CRUD operations within DB
# Without directly using SQL Queries

class Post(Base):
    __tablename__ = "posts_2"
    __table_args__ = {'schema': 'fastapi-db'}

    id = Column(String(6), primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    owner_id = Column(Integer,
                    ForeignKey("fastapi-db.users_2.id",
                    ondelete="CASCADE"),
                    nullable = False)


class User(Base):
    __tablename__ = "users_2"
    __table_args__ = {'schema': 'fastapi-db'}
    id = Column(Integer, primary_key=True, nullable=False, unique = True)
    email = Column(String, nullable = False, unique = True)
    password = Column(String, nullable=False)
    createdAt = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))

# User can only like a post once
# Create new table likes
# primary key = post id + user id
#
class Likes(Base):
    __tablename__ = "likes_2"
    __table_args__ = {'schema': 'fastapi-db'}
    post_id = Column(String, ForeignKey("fastapi-db.posts_2.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("fastapi-db.users_2.id"), primary_key=True)
