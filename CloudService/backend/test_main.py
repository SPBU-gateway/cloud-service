import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import models
from databases import Database

DB_URL = "postgresql://postgres:1234@localhost:5432/CyberImmunity"

test_data = [{"name": "test_name", "ip": "test_ip", "category": "test_device"}]


@pytest.fixture
def test_db():
    engine = create_engine(DB_URL)
    test_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    test_db = test_session_local()
    models.Base.metadata.create_all(bind=engine)

    yield test_db

    test_db.rollback()


@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_init(client, test_db):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"data": "Hello world!"}


def test_create_device(client, test_db):
    response = client.post("/devices", json=test_data[0])
    assert response.status_code == 200


def test_read_device(client, test_db):
    response = client.get(f"devices/{test_data[0]['name']}")
    assert response.status_code == 200
    assert response.json()["id"] is not None
    assert response.json()["name"] == test_data[0]["name"]
    assert response.json()["category"] == test_data[0]["category"]
    assert response.json()["ip"] == test_data[0]["ip"]


def test_update_device(client, test_db):
    response = client.get(f"devices/{test_data[0]['name']}")
    assert response.status_code == 200

    response = client.patch(f"devices/{response.json()['id']}", json={"name": "test_name1"})
    assert response.status_code == 200
    assert response.json()["name"] == "test_name1"
    assert response.json()["category"] == test_data[0]["category"]
    assert response.json()["ip"] == test_data[0]["ip"]
    response = client.patch(f"devices/{response.json()['id']}", json={"name": test_data[0]['name']})
    assert response.status_code == 200
    assert response.json()["name"] == test_data[0]['name']
    assert response.json()["category"] == test_data[0]["category"]
    assert response.json()["ip"] == test_data[0]["ip"]


def test_delete_device(client, test_db):
    session = test_db
    temp = test_data[0]
    response = client.get(f"devices/{test_data[0]['name']}")
    assert response.status_code == 200
    session.query(models.Device).filter(models.Device.name == temp["name"] and models.Device.ip == temp["ip"]
                                        and models.Device.category == temp["category"]).delete()
    session.commit()
    response = client.get(f"devices/{test_data[0]['name']}")
    assert response.status_code == 404
