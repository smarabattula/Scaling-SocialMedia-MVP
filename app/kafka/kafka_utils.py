from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic
from ..config import settings
import uuid
def get_producer_config():
    return {'bootstrap.servers': f'localhost:{settings.kafka_port}'}

def setup_producer():
    producer = Producer(get_producer_config())
    return producer

def add_kafka_topic(topic_name = settings.kafka_posts_topic):
    admin_client = AdminClient(get_producer_config())
    metadata = admin_client.list_topics(timeout=10)

    if topic_name not in metadata.topics:
        topic_list = [NewTopic(topic_name, num_partitions=2, replication_factor=2)]
        admin_client.create_topics(topic_list)
        print(f"Topic '{topic_name}' created.")
    else:
        print(f"Topic '{topic_name}' already exists.")

def get_consumer_config():
    return {
        'bootstrap.servers': f'localhost:{settings.kafka_port}',
        'group.id': f'posts-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    }

def setup_consumer(topic_name = settings.kafka_posts_topic):
    print(f"Consumer config:{get_consumer_config()}")
    consumer = Consumer(get_consumer_config())
    consumer.subscribe([topic_name])
    return consumer
