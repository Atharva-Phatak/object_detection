import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from counter.adapters.count_repo import SQLObjectCountRepo
from counter.adapters.sql_models import Base
from counter.domain.models import ObjectCount


def _db_url() -> URL:
    return URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER", "counter"),
        password=os.getenv("DB_PASSWORD", "secret"),
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        database=os.getenv("MYSQL_DB", "object_counts"),
    )


@pytest.fixture(scope="session")
def engine():
    return create_engine(_db_url())


@pytest.fixture(autouse=True)
def setup_teardown(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def repo():
    return SQLObjectCountRepo(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        database=os.getenv("MYSQL_DB", "object_counts"),
    )


@pytest.mark.integration
class TestSQLObjectCountRepo:
    def test_update_and_read_values(self, repo):
        repo.update_values([ObjectCount(object_class="cat", count=2)])
        result = repo.read_values()
        assert result == [ObjectCount(object_class="cat", count=2)]

    def test_accumulates_counts(self, repo):
        repo.update_values([ObjectCount(object_class="cat", count=2)])
        repo.update_values([ObjectCount(object_class="cat", count=3)])
        result = repo.read_values()
        assert result == [ObjectCount(object_class="cat", count=5)]

    def test_read_filtered_by_class(self, repo):
        repo.update_values(
            [
                ObjectCount(object_class="cat", count=2),
                ObjectCount(object_class="dog", count=1),
            ]
        )
        result = repo.read_values(object_classes=["cat"])
        assert result == [ObjectCount(object_class="cat", count=2)]

    def test_read_empty(self, repo):
        result = repo.read_values()
        assert result == []
