from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

for _ in range(10):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        break
    except NoBrokersAvailable:
        print("Kafka broker not available, retrying...")
        time.sleep(10)
else:
    raise RuntimeError("Kafka is not available after several attempts")

def send_event(topic, event):
    try:
        producer.send(topic, event)
        producer.flush()
        print(f"[Kafka] Sent to {topic}: {event}")
    except Exception as e:
        print(f"[Kafka] Error sending to {topic}: {e}")
