import asyncio
import redis
from contextlib import asynccontextmanager
from redis.commands.json.path import Path
from . import schemas

@asynccontextmanager
async def redis_session():
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    try:
        yield r
    finally:
        r.close()

async def init_redis():
    from redis.commands.search.field import NumericField, TextField, TagField
    from redis.commands.search.indexDefinition import IndexDefinition, IndexType
    async with redis_session() as r:
        schema = (
            TextField("$.id", as_name="id"),
            TextField("$.title", as_name="title"),
            TextField("$.content", as_name="content"),
            NumericField("$.owner_id", as_name="owner_id"),
            NumericField("$.likes", as_name="likes"),
            TagField("$.published", as_name="published"),  # boolean
            NumericField("$.createdAt", as_name="createdAt")
        )

        index = r.ft("posts")
        index.create_index(
            schema,
            definition=IndexDefinition(prefix=["post:"], index_type=IndexType.JSON),
        )

async def update_like_count(id, is_like = True):
    async with redis_session() as r:
        key = f"post:{id}"
        if r.get(key):
            val = 1 if is_like else -1
            r.json().numincrby(key, Path("$.likes"), val)

async def save_post_to_redis(post_out: schemas.PostOut):
    async with redis_session() as r:
        post_dict = post_out.model_dump()
        post_dict["createdAt"] = post_dict["createdAt"].timestamp()  # Convert datetime to timestamp
        post_dict["published"] = "1" if post_dict["published"] else "0"  # Convert boolean to string
        r.json().set(f"post:{post_out.id}", Path.root_path(), post_dict)

async def process_post_on_redis(post, likes, current_user_id = None):
    # Construct full response object
    post_out = schemas.PostOut(
        id=post.id, title=post.title, content=post.content,
        published=post.published, createdAt=post.createdAt,
        owner_id=post.owner_id if hasattr(post, "owner_id") else current_user_id,
        likes=likes
    )
    save_data_to_redis = asyncio.create_task(save_post_to_redis(post_out))
    # Post Data to Redis Cache
    await save_data_to_redis
    return post_out
