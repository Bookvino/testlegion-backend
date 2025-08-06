import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Select correct database URL based on environment flag
if os.getenv("DIGITALOCEAN") == "true":
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    DATABASE_URL = os.getenv("LOCAL_DATABASE_URL")

# Raise an error if no database URL is set
if not DATABASE_URL:
    raise ValueError("No database URL found. Please check your .env file.")

# Create connection to PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal = used to create DB sessions in endpoints
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = shared base class for all models
Base = declarative_base()


