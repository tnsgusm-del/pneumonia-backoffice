<<<<<<< HEAD
import os
import sys
from urllib.parse import quote_plus
from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from alembic import context

# 프로젝트 루트를 sys.path에 추가하여 app 모듈을 임포트할 수 있게 함
sys.path.append(os.getcwd())

from app.core.db.databases import Base
# autogenerate가 모델 스키마를 정상 추적할 수 있도록 임포트 유지
from app.models.user import User
from app.models.patient import Patient
from app.models.analysis import Analysis
import app.models
=======
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.core.db.databases import Base
import app.models

>>>>>>> main

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

<<<<<<< HEAD
# Model의 MetaData 등록
target_metadata = Base.metadata

=======
# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

>>>>>>> main

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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
<<<<<<< HEAD
    # 1. 환경 변수에서 DB 접속 정보 가져오기
    db_user = os.getenv("DB_USER", "root")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "pneumonia")
    
    # 🔥 [종현님 핵심 코드] 특수문자(@, !) 충돌을 막기 위해 quote_plus로 패스워드 감싸기
    raw_password = os.getenv("DB_PASSWORD", "Password123@!")
    db_pass = quote_plus(raw_password) 
    
    # 2. [main 요구사항 반영] 동기식 마이그레이션을 위해 pymysql 드라이버 주소 조립
    sync_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    # 3. 동기식 엔진 생성 및 연결
    connectable = create_engine(sync_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

=======
    from app.core.config import settings
    from sqlalchemy import create_engine
    
    # settings.DATABASE_URL을 직접 사용하여 동기식 엔진을 만듭니다.
    # Aiven MySQL 사용을 위해 URL을 pymysql 드라이버로 변환합니다.
    sync_url = settings.DATABASE_URL.replace("mysql+asyncmy://", "mysql+pymysql://")
    
    connectable = create_engine(sync_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

>>>>>>> main
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
<<<<<<< HEAD
```
eof

---
=======
>>>>>>> main
