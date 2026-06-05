import os
from urllib.parse import quote_plus  # 👈 여기에 안전하게 추가!

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 프로젝트 루트를 sys.path에 추가하여 app 모듈을 임포트할 수 있게 함
import os
import sys
sys.path.append(os.getcwd())

from app.core.db.databases import Base, DATABASE_URL

# Model Import
from app import models

# Alembic Config object
config = context.config

# Alembic 설정 파일의 sqlalchemy.url을 우리 앱의 DATABASE_URL로 덮어씁니다.
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# model's MetaData object
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # 1. 환경 변수에서 DB 접속 정보 가져오기
    db_user = os.getenv("DB_USER", "root")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "pneumonia")
    
    # 🔥 [핵심] 특수문자(@, !) 충돌을 막기 위해 quote_plus로 패스워드 감싸기
    raw_password = os.getenv("DB_PASSWORD", "Password123@!")
    db_pass = quote_plus(raw_password) 
    
    # 2. 안전하게 치환된 비밀번호로 비동기 MySQL URL 주소 조립
    DATABASE_URL = f"mysql+asyncmy://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    # 3. alembic.ini의 설정을 쓰는 대신, 우리가 직접 만든 DATABASE_URL로 비동기 엔진 생성
    from sqlalchemy.ext.asyncio import create_async_engine
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    # 4. 기존 Alembic의 마이그레이션 실행 로직 수행
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
