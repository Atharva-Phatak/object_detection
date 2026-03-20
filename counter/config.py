import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects
from counter.adapters.count_repo import SQLObjectCountRepo


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def prod_count_action(model_name: str) -> CountDetectedObjects:
    tfs_host = os.environ.get("TFS_HOST", "localhost")
    tfs_port = os.environ.get("TFS_PORT", 8501)
    mongo_host = os.environ.get("MONGO_HOST", "localhost")
    mongo_port = os.environ.get("MONGO_PORT", 27017)
    mongo_db = os.environ.get("MONGO_DB", "prod_counter")
    return CountDetectedObjects(
        TFSObjectDetector(tfs_host, tfs_port, model_name),
        CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db),
    )


def sql_count_action(model_name: str) -> CountDetectedObjects:
    tfs_host = os.environ.get("TFS_HOST", "localhost")
    tfs_port = int(os.environ.get("TFS_PORT", 8501))
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    mysql_port = int(os.environ.get("MYSQL_PORT", 3306))
    mysql_db = os.environ.get("MYSQL_DB", "object_counts")
    return CountDetectedObjects(
        TFSObjectDetector(tfs_host, tfs_port, model_name),
        SQLObjectCountRepo(host=mysql_host, port=mysql_port, database=mysql_db),
    )


def prod_predictions_action(model_name: str) -> CountDetectedObjects:
    tfs_host = os.environ.get("TFS_HOST", "localhost")
    tfs_port = int(os.environ.get("TFS_PORT", 8501))
    return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, model_name))


def get_predictions_action(model_name: str) -> CountDetectedObjects:
    env = os.environ.get("ENV", "dev")
    predictions_action_fn = f"{env}_predictions_action"
    return globals()[predictions_action_fn](model_name=model_name)


def get_count_action(model_name: str) -> CountDetectedObjects:
    env = os.environ.get("ENV", "dev")
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn](model_name=model_name)
