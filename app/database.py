from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Læs forbindelsesstreng fra .env-filen
DATABASE_URL = os.getenv("DATABASE_URL")

# Opret forbindelse til PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal = bruges til at oprette db-sessioner i dine endpoints
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = fælles baseklasse for alle dine modeller (fx User)
Base = declarative_base()

