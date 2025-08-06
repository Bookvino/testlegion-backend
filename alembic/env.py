import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# -------------------------
# Add project root to sys.path so we can import "app"
# -------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()

# -------------------------
# Alembic Config object
# -------------------------
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------
# Select correct DB URL based on environment flag
# -------------------------
if os.getenv("DIGITALOCEAN") == "true":
    db_url = os.getenv("DATABASE_URL")
else:
    db_url = os.getenv("LOCAL_DATABASE_URL")

if not db_url:
    raise Exception("⚠️ No database URL found. Please check your .env file.")

config.set_main_option("sqlalchemy.url", db_url)

# -------------------------
# Import Base and all models so Alembic can detect tables
# -------------------------
from app.database import Base
from app.models.pagespeed_analysis import PageSpeedAnalysis  # noqa: F401
from app.models.user import User  # noqa: F401

# Metadata for autogenerate support
target_metadata = Base.metadata

# -------------------------
# Run migrations offline
# -------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# -------------------------
# Run migrations online
# -------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# -------------------------
# Start migrations
# -------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
