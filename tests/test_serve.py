from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient
from src import serve


@pytest.fixture
def client(monkeypatch):
    model = Mock()
    model.predict.return_value = [1]
    monkeypatch.setattr(serve, "download_model", lambda: None)
    monkeypatch.setattr(serve.joblib, "load", lambda path: model)
    with TestClient(serve.app) as client:
        yield client, model


def test_health_and_prediction(client):
    api, model = client
    assert api.get("/healthz").json() == {"status": "ok"}
    response = api.post("/score", json={"features": [28, 2, 14, 2, 11, 0, 1, 0, 0, 45]})
    assert response.status_code == 200
    assert response.json() == {"prediction": 1, "label": "thu_nhap_cao"}
    assert list(model.predict.call_args.args[0].columns) == serve.FEATURE_NAMES
    model.predict.return_value = [0]
    assert api.post("/score", json={"features": [0]*10}).json()["label"] == "thu_nhap_thap"


def test_reject_wrong_feature_count(client):
    api, model = client
    assert api.post("/score", json={"features": [1, 2]}).status_code == 400
    model.predict.assert_not_called()
