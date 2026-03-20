import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import URL
from alembic import context
from counter.adapters.sql_models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    # Allow passing URL directly via -x db_url=...
    x_args = context.get_x_argument(as_dictionary=True)
    if "db_url" in x_args:
        return x_args["db_url"]

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    if not db_user or not db_password:
        raise ValueError("DB_USER and DB_PASSWORD environment variables must be set")

    return URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_password,
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        database=os.getenv("MYSQL_DB", "object_counts"),
    )


def run_migrations_online():
    connectable = create_engine(get_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
