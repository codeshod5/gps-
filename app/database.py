import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
ele = os.getenv("db_url")

database_url = ele
engine = create_engine(database_url)

def create_tables():
    from models import SQLModel  # Import models before creating tables
    SQLModel.metadata.create_all(engine)
create_tables()

def get_session():
    with Session(engine) as session:
        yield session
app = FastAPI()
