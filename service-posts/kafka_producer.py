from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

_producer = None

def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
    return _producer

def send_event(topic, event):
    print(f"[Kafka] Sending to {topic}: {event}")
    producer = get_producer()
    producer.send(topic, event)
    producer.flush()
