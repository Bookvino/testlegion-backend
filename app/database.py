from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Please define it in your environment or .env file.")

# Opret forbindelse til PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal = bruges til at oprette db-sessioner i dine endpoints
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = fælles baseklasse for alle dine modeller (fx User)
Base = declarative_base()

