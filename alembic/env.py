import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import URL
from alembic import context
from counter.adapters.sql_models import Base

config = context.config

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

if not db_user or not db_password:
    raise ValueError("DB_USER and DB_PASSWORD environment variables must be set")

config.set_main_option(
    "sqlalchemy.url",
    str(
        URL.create(
            drivername="mysql+pymysql",
            username=db_user,
            password=db_password,
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            database=os.getenv("MYSQL_DB", "object_counts"),
            query={"auth_plugin": "mysql_native_password"},
        )
    ),
)

target_metadata = Base.metadata

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
