import os
import pytest
from pymongo import MongoClient
from counter.adapters.count_repo import CountMongoDBRepo
from counter.domain.models import ObjectCount


@pytest.fixture(scope="session")
def mongo_client():
    return MongoClient(
        host=os.getenv("MONGO_HOST", "localhost"),
        port=int(os.getenv("MONGO_PORT", 27017)),
    )


@pytest.fixture(autouse=True)
def setup_teardown(mongo_client):
    yield
    mongo_client[os.getenv("MONGO_DB", "test_counter")].counter.drop()


@pytest.fixture
def repo():
    return CountMongoDBRepo(
        host=os.getenv("MONGO_HOST", "localhost"),
        port=int(os.getenv("MONGO_PORT", 27017)),
        database=os.getenv("MONGO_DB", "test_counter"),
    )


@pytest.mark.integration
class TestMongoObjectCountRepo:
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
