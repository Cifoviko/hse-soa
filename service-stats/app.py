from kafka_consumer import run_consumer
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/statistics")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Initializing DB...")
    init_db()
    print("Starting Kafka consumer...")
    run_consumer()
