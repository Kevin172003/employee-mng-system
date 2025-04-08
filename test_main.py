from fastapi.testclient import TestClient
from auth import require_admin
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from dependencies import get_db
from models import User
from test_routes import SQLALCHEMY_DATABASE_URL, engine, TestingSessionLocal, override_get_db


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[require_admin] = lambda: None

client = TestClient(app=app)

# Ensure test DB tables are created before test runs
def setup_module(module):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add_all([
        User(username="admin", hashed_password="hashedpassword", role="admin"),
        User(username="Kevin", hashed_password="hashedpassword123", role="viewer"),
    ])
    db.commit()
    db.close()

def teardown_module(module):
    Base.metadata.drop_all(bind=engine)



######### Register ##########

def test_register():
    payload = {
        "username":"admin123",
        "password":"admin123",
        "role":"admin",
    }
    response = client.post("/register",json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "User created successfully"




######### Login ##########

def test_login():
    payload = {
        "username":"admin123",
        "password":"admin123",
    }
    response = client.post("/login", data=payload)
    assert response.status_code == 200



# For UI-Check
def test_login_form_loads():
    response = client.get("/login")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
def test_register_form_loads():
    response = client.get("/register")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]



######### login token ############

def test_login_success():
    client.post("/register", json={
        "username": "testuser",
        "password": "testpass",
        "role": "admin"
    })

    response = client.post("/token",
                           data={"username":"testuser",
                                 "password": "testpass"},
                            headers={"content-type": "application/x-www-form-urlencoded"})
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_fail():
    response = client.post(
        "/token",
        data={"username": "wrong", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 400