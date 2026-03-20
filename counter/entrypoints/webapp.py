from io import BytesIO

from flask import Flask, request, jsonify

from counter import config


def create_app():
    app = Flask(__name__)

    count_action = config.get_count_action()

    @app.route("/object-count", methods=["POST"])
    def object_detection():
        threshold = float(request.form.get("threshold", 0.5))
        uploaded_file = request.files["file"]
        image = BytesIO()
        uploaded_file.save(image)
        count_response = count_action.execute(image, threshold)
        return jsonify(count_response)

    @app.route("/predictions", methods=["POST"])
    def predictions():
        threshold = float(request.form.get("threshold", 0.5))
        image = BytesIO()
        request.files["file"].save(image)
        preds = count_action.find_predictions(image, threshold)
        return jsonify([p.model_dump() for p in preds])

    return app


if __name__ == "__main__":
    app = create_app()
    app.run("0.0.0.0", debug=True)
