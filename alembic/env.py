import os
import sys
from urllib.parse import quote_plus
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from alembic import context

sys.path.append(os.getcwd())

from app.core.db.databases import Base
from app.models.user import User
from app.models.patient import Patient
from app.models.analysis import Analysis
from app.models.medical_record import MedicalRecord
from app.models.xray_image import XrayImage
from app.models.ai_analysis_result import AiAnalysisResult

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


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


def run_migrations_online() -> None:
    db_user = os.getenv("DB_USER", "ozcoding")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3307")
    db_name = os.getenv("DB_NAME", "ai_health")
    
    raw_password = os.getenv("DB_PASSWORD", "pw1234")
    db_pass = quote_plus(raw_password)

    sync_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    connectable = create_engine(sync_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()