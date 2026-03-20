from http import HTTPStatus
from io import BytesIO

from flask import Flask, request, jsonify

from counter import config

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def _get_image() -> BytesIO:
    if "file" not in request.files:
        raise ValueError("No file provided")
    uploaded_file = request.files["file"]
    if uploaded_file.filename.rsplit(".", 1)[-1].lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file type, allowed types are {ALLOWED_EXTENSIONS}")
    image = BytesIO()
    uploaded_file.save(image)
    return image


def _get_threshold() -> float:
    threshold = float(request.form.get("threshold", 0.5))
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"Threshold must be between 0 and 1, got {threshold}")
    return threshold


def create_app():
    app = Flask(__name__)

    @app.route("/object-count", methods=["POST"])
    def object_detection():
        try:
            image = _get_image()
            threshold = _get_threshold()
            model_name = request.form.get("model_name", "ssd_mobilenet_v2")
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
        count_action = config.get_count_action(model_name)
        return jsonify(count_action.execute(image, threshold).model_dump())

    @app.route("/predictions", methods=["POST"])
    def predictions():
        try:
            image = _get_image()
            threshold = _get_threshold()
            model_name = request.form.get("model_name", "ssd_mobilenet_v2")
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
        preds = config.get_predictions_action(model_name).find_predictions(
            image, threshold
        )
        return jsonify([p.model_dump() for p in preds])

    return app


if __name__ == "__main__":
    app = create_app()
    app.run("0.0.0.0", debug=True)
