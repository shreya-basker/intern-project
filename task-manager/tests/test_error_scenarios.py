from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_value_error():
    response = client.get("/test/value-error")
    assert response.status_code == 500


def test_zero_division():
    response = client.get("/test/zero-division")
    assert response.status_code == 500


def test_key_error():
    response = client.get("/test/key-error")
    assert response.status_code == 500


def test_index_error():
    response = client.get("/test/index-error")
    assert response.status_code == 500


def test_type_error():
    response = client.get("/test/type-error")
    assert response.status_code == 500


def test_attribute_error():
    response = client.get("/test/attribute-error")
    assert response.status_code == 500


def test_file_error():
    response = client.get("/test/file-error")
    assert response.status_code == 500
