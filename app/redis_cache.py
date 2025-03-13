import asyncio
import redis
from contextlib import asynccontextmanager
from redis.commands.json.path import Path
from . import schemas

LRU_CACHE_KEY = "lru_cache_key"
MAX_CACHE_SIZE = 100

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

async def update_like_count(id, is_like=True):
    async with redis_session() as r:
        key = f"post:{id}"

        # Use pipeline for atomic operations
        async with r.pipeline(transaction=True) as pipe:
            # Increment the like count or initialize it
            val = 1 if is_like else -1
            exists = await r.exists(key)

            if exists:
                await pipe.json().numincrby(key, Path("$.likes"), val)
            else:
                initial_data = {"likes": 1 if is_like else 0}
                await pipe.json().set(key, Path.root_path(), initial_data)

            await pipe.expire(key, 3600)  # Reset TTL to 1 hour on update

            # Efficient LRU eviction logic using LMOVE (Redis 6.2+)
            await pipe.lrem(LRU_CACHE_KEY, 0, key)  # Remove key if already present
            await pipe.rpush(LRU_CACHE_KEY, key)     # Add key to end of LRU list

            # Eviction logic in the same transaction
            if await r.llen(LRU_CACHE_KEY) >= MAX_CACHE_SIZE:
                oldest_key = await pipe.lpop(LRU_CACHE_KEY)
                await pipe.delete(oldest_key)

            await pipe.execute()

async def save_post_to_redis(post_out: schemas.PostOut):
    async with redis_session() as r:
        post_dict = post_out.model_dump()
        post_dict["createdAt"] = post_dict["createdAt"].timestamp()  # Convert datetime to timestamp
        post_dict["published"] = "1" if post_dict["published"] else "0"  # Convert boolean to string
        key = f"post:{post_out.id}"
        r.json().set(key, Path.root_path(), post_dict)
        r.expire(key, 3600)  # Set TTL to 1 hour

async def process_post_on_redis(post, likes, current_user_id=None):
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
