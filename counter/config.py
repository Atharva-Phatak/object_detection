import os

from counter.adapters.count_repo import (
    CountInMemoryRepo,
    CountMongoDBRepo,
    ObjectCountRepo,
    SQLObjectCountRepo,
)
from counter.adapters.object_detector import FakeObjectDetector, TFSObjectDetector
from counter.domain.actions import CountDetectedObjects


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def _build_detector(model_name: str) -> TFSObjectDetector:
    env = os.environ.get("ENV", "dev")
    if env == "dev":
        return FakeObjectDetector()
    tfs_host = os.environ.get("TFS_HOST", "localhost")
    tfs_port = int(os.environ.get("TFS_PORT", 8501))
    return TFSObjectDetector(tfs_host, tfs_port, model_name)


def _build_repo() -> ObjectCountRepo:
    env = os.environ.get("ENV", "dev")
    if env == "prod":
        return CountMongoDBRepo(
            host=os.environ.get("MONGO_HOST", "localhost"),
            port=int(os.environ.get("MONGO_PORT", 27017)),
            database=os.environ.get("MONGO_DB", "prod_counter"),
        )
    if env == "sql":
        return SQLObjectCountRepo(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", 3306)),
            database=os.environ.get("MYSQL_DB", "object_counts"),
        )
    return CountInMemoryRepo()


def get_count_action(model_name: str) -> CountDetectedObjects:
    return CountDetectedObjects(_build_detector(model_name), _build_repo())


def get_predictions_action(model_name: str) -> CountDetectedObjects:
    return CountDetectedObjects(_build_detector(model_name))
