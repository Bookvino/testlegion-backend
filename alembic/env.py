import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Tilføj projektmappen til stien, så 'app' kan importeres
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Indlæs .env-variabler
from dotenv import load_dotenv
load_dotenv()

# Alembic Config
config = context.config

# Log-konfiguration (valgfrit)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sæt database-url dynamisk fra .env
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise Exception("⚠️ DATABASE_URL ikke fundet i .env-filen")
config.set_main_option("sqlalchemy.url", db_url)

# Importér dine modeller og metadata
from app.database import Base
from app.models import pagespeed_analysis, user  # Tilføj andre modeller her

target_metadata = Base.metadata

# Offline migration
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# Online migration
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# Start migration
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
