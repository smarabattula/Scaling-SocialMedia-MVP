from app import models
from confluent_kafka import Consumer, Producer
from ..config import settings
from sqlalchemy.orm import Session
import time
import json
from ..utils import generate_base62_id
import asyncio
from app.database import SessionLocal
db = SessionLocal()

async def save_to_db(post, current_user_id, db: Session):
    try:
        post = json.loads(post)
        new_post = models.Post(**post)
        new_post.owner_id = current_user_id
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        print(new_post.id, new_post.title, new_post.content)
        return new_post
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()

async def write_post(kafka_producer: Producer, message: str, current_user, topic_name: str = settings.kafka_posts_topic):
    key = str(current_user.id)
    kafka_producer.produce(topic_name, key=f"{key}_{time.time()}", value=message)
    kafka_producer.flush()
    time.sleep(5)

async def poll_posts(kafka_consumer: Consumer, db: Session):
    try:
        while True:  # Continuous polling loop
            msg = kafka_consumer.poll(timeout=10)

            if msg is None:
                print("No messages yet.")
                continue

            if msg.error():
                print(f"Message Error: {msg.error()}")
                continue

            key = msg.key().decode('utf-8').split("_")[0]
            current_user_id = int(key)

            await save_to_db(msg.value().decode('utf-8'), current_user_id=current_user_id, db=db)
            print(f"Received: {msg.value().decode('utf-8')}")

            commit_result = kafka_consumer.commit(message=msg, asynchronous=False)


            await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
