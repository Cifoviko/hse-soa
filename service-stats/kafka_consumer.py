from kafka import KafkaConsumer
import json
import os
from models import SessionLocal, Event

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPICS = ["user_registrations", "post_views", "likes", "comments", "clicks"]

def run_consumer():
    consumer = KafkaConsumer(
        *TOPICS,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='statistics_group'
    )

    db = SessionLocal()

    try:
        for message in consumer:
            print(f"[Kafka] Got message from topic {message.topic}: {message.value}")
            event = Event(topic=message.topic, data=message.value)
            db.add(event)
            db.commit()
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        db.close()
