# NIQ Innovation Enablement - Object Counter Challenge

The goal of this repo is to demonstrate how to apply Hexagonal Architecture in a ML based system.

This application consists of a Flask API that receives an image and a threshold and returns the number of objects detected in the image, along with a predictions endpoint that returns raw detection results.

The application is composed of three layers:

- **entrypoints**: Exposes the API and receives the requests. Responsible for validating requests and returning responses.
- **adapters**: Communicates with external services. Translates domain objects to external service objects and vice-versa.
- **domain**: Business logic. Orchestrates calls to external services and applies business rules.

The model used in this example has been taken from [Kaggle](https://www.kaggle.com/models/google/mobilenet-v2/tensorFlow1/openimages-v4-ssd-mobilenet-v2/1).

---

## What was added

### Task 1 — New `/predictions` endpoint
A new `POST /predictions` endpoint was added that receives an image and threshold and returns a list of `Prediction` domain objects (class, score, box) that exceed the threshold. Unlike `/object-count`, this endpoint is stateless — it does not persist anything to the database.

### Task 2 — MySQL adapter
A new `SQLObjectCountRepo` adapter was added implementing `ObjectCountRepo` using SQLAlchemy + PyMySQL. Schema is managed via **Alembic** — migration files are committed to the repo and `alembic upgrade head` runs automatically on container startup before Flask starts.

### Task 3 & 4 — Improvements proposed and implemented
- Migrated dependency management from `requirements.txt` to `uv` with `pyproject.toml`
- Replaced `dataclasses` with Pydantic `BaseModel` for automatic validation and serialization
- Added proper input validation and error handling in Flask endpoints (400 for missing file, invalid threshold, invalid file type)
- Replaced `__debug__` pattern with structured logging
- Added pre-commit hooks with ruff for linting
- Added `Dockerfile` using official uv image with intermediate caching layers and multi-platform builds (`amd64` + `arm64`)
- Added `docker-compose.yaml` with profiles (`sql`, `prod`, `test`) so only relevant services start per environment
- Added model download script with idempotency check — skips download if model already exists
- Added `model-downloader` service in docker-compose that runs before TFServing
- Added `Makefile` consolidating all tasks
- Added GitHub Actions CI pipeline building and pushing to `ghcr.io` on merge to main
- Added `.env` / `.env.example` for credential management

### Task 5 — Multiple internally trained models
The current setup supports multiple internally trained models — the `/predictions` and `/object-count` endpoints accept a `model_name` parameter, and TFServing routes to the correct model via `/v1/models/{model_name}:predict`. Each additional model requires its own TFServing service in docker-compose with a different port and label map. No domain layer changes are required.

### Task 6 — Testing and framework support
**Integration and E2E tests:**
- Unit tests with mocks covering all domain logic
- Integration tests for `SQLObjectCountRepo` and `CountMongoDBRepo` against real databases, marked `@pytest.mark.integration` and skipped locally by default
- E2E API tests covering happy path, error cases, and verifying `/predictions` has no side effects on stored counts
- CI runs integration tests via docker-compose `--profile test`

**Additional framework support (outlined):**
The hexagonal architecture makes adding new ML frameworks straightforward - only a new `ObjectDetector` adapter is needed and which can be later linked up in the config.py fill. Full testing is limited by available RAM locally - a production implementation would require dedicated infrastructure per framework (e.g. TorchServe container for PyTorch).

---

## Prerequisites

Copy the example .env.example file and fill in credentials:


Install dependencies:

```bash
make setup
```

---

## Download the model

```bash
make download-model
```

This only needs to be done once. The script skips the download if the model already exists.

By the end you should have the following structure:
```
tmp/
  model/
    ssd_mobilenet_v2/
        1/
            saved_model.pb
```

---

## Run the application

### Development mode (fake detector, in-memory repo)

```bash
make run-dev
```

### Production mode with MongoDB

```bash
make run-prod
```

### Production mode with MySQL

```bash
make run-sql
```

> [!TIP]
> If you face service connectivity issues on Windows, try replacing `localhost` with `127.0.0.1` globally.

---

## Call the service

### Object count endpoint

```bash
curl -F "threshold=0.9" -F "model_name=ssd_mobilenet_v2" -F "file=@resources/images/boy.jpg" http://localhost:5001/object-count
curl -F "threshold=0.9" -F "model_name=ssd_mobilenet_v2" -F "file=@resources/images/cat.jpg" http://localhost:5001/object-count
curl -F "threshold=0.9" -F "model_name=ssd_mobilenet_v2" -F "file=@resources/images/food.jpg" http://localhost:5001/object-count
```

### Predictions endpoint

```bash
curl -F "threshold=0.9" -F "model_name=ssd_mobilenet_v2" -F "file=@resources/images/boy.jpg" http://localhost:5001/predictions
curl -F "threshold=0.9" -F "model_name=ssd_mobilenet_v2" -F "file=@resources/images/cat.jpg" http://localhost:5001/predictions
curl -F "threshold=0.9" -F "model_name=ssd_mobilenet_v2" -F "file=@resources/images/food.jpg" http://localhost:5001/predictions
```

`model_name` defaults to `ssd_mobilenet_v2` if not provided.

---

## Run the tests

### Unit and E2E tests (no external services needed)

```bash
make test
```

### Integration tests (requires MySQL and MongoDB)
run:

```bash
make test-integration
```

---

## Stop services

```bash
make stop
```

To stop and remove all volumes:

```bash
make clean
```
