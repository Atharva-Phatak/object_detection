import io
from pathlib import Path

import pytest

from counter.entrypoints.webapp import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def image_path():
    ref_dir = Path(__file__).parent
    return ref_dir.parent.parent / "resources" / "images" / "boy.jpg"


def _post(client, endpoint: str, image_path=None, threshold: str = "0.9"):
    data = {"threshold": threshold, "model_name": "ssd_mobilenet_v2"}
    if image_path:
        with open(image_path, "rb") as f:
            data["file"] = (io.BytesIO(f.read()), "test.jpg")
    return client.post(
        endpoint, data=data, content_type="multipart/form-data", buffered=True
    )


class TestObjectCountEndpoint:
    def test_returns_200_with_valid_input(self, client, image_path):
        assert _post(client, "/object-count", image_path).status_code == 200

    def test_response_contains_current_and_total_objects(self, client, image_path):
        body = _post(client, "/object-count", image_path).get_json()
        assert "current_objects" in body
        assert "total_objects" in body

    def test_missing_file_returns_400(self, client):
        response = client.post(
            "/object-count",
            data={"threshold": "0.5"},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_invalid_threshold_returns_400(self, client, image_path):
        assert (
            _post(client, "/object-count", image_path, threshold="2.0").status_code
            == 400
        )

    def test_invalid_file_type_returns_400(self, client):
        data = {"threshold": "0.5", "file": (io.BytesIO(b"not an image"), "test.txt")}
        response = client.post(
            "/object-count", data=data, content_type="multipart/form-data"
        )
        assert response.status_code == 400

    def test_high_threshold_returns_empty_current_objects(self, client, image_path):
        body = _post(client, "/object-count", image_path, threshold="1.0").get_json()
        assert body["current_objects"] == []


class TestPredictionsEndpoint:
    def test_returns_200_with_valid_input(self, client, image_path):
        assert _post(client, "/predictions", image_path).status_code == 200

    def test_returns_list(self, client, image_path):
        assert isinstance(_post(client, "/predictions", image_path).get_json(), list)

    def test_prediction_has_required_fields(self, client, image_path):
        predictions = _post(client, "/predictions", image_path).get_json()
        assert len(predictions) > 0
        for pred in predictions:
            assert "class_name" in pred
            assert "score" in pred
            assert "box" in pred

    def test_box_has_all_coordinates(self, client, image_path):
        pred = _post(client, "/predictions", image_path).get_json()[0]
        assert all(k in pred["box"] for k in ("xmin", "ymin", "xmax", "ymax"))

    def test_high_threshold_returns_empty_list(self, client, image_path):
        assert (
            _post(client, "/predictions", image_path, threshold="1.0").get_json() == []
        )

    def test_missing_file_returns_400(self, client):
        response = client.post(
            "/predictions",
            data={"threshold": "0.5"},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_invalid_threshold_returns_400(self, client, image_path):
        assert (
            _post(client, "/predictions", image_path, threshold="2.0").status_code
            == 400
        )

    def test_predictions_not_persisted(self, client, image_path):
        """Calling /predictions should not affect /object-count totals."""
        _post(client, "/predictions", image_path)
        body = _post(client, "/object-count", image_path).get_json()
        total = {o["object_class"]: o["count"] for o in body["total_objects"]}
        assert total.get("cat") == 1
