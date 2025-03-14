from app.kafka import kafka_init, kafka_processing
import asyncio
from app.database import SessionLocal

kafka_inst = kafka_init.Kafka()
kafka_inst.add_topic()
producer, consumer = kafka_inst.producer, kafka_inst.consumer

db = SessionLocal()

# class User:
#     def __init__(self, id):
#         self.id = id

# message ={
#     "title": "post about Man Utd",
#     "content": "Bruno Scored another pen! Its 15 for the season for Bruno!"
#     }

async def main():
    # user = User(14)
    # await kafka_processing.write_post(producer, json.dumps(message), user)
    await kafka_processing.poll_posts(consumer, db)

asyncio.run(main())
