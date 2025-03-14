from .kafka_utils import add_kafka_topic, setup_producer, setup_consumer
# Initialize Kafka Topic, Producer and Consumers

class Kafka:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Kafka, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.producer = setup_producer()
            self.consumer = setup_consumer()

    def add_topic(self):
        add_kafka_topic()
        return

