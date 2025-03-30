import time
import pytest
from flask import json
import os
from app import app, db, User, get_hashed_password
    
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# ------====== [CALLS WITH INVALID DATA] =====-----

def test_register_missing_data(client):
    response = client.post("/register", json={})
    assert response.status_code == 400
    assert response.json["msg"] == "Missing username or password"

def test_register_invalid_data(client):
    response = client.post("/register", json={"username": "us", "password": "weak"})
    assert response.status_code == 401
    assert response.json["msg"] == "Password is invalid"
    
    response = client.post("/register", json={"username": "us", "password": "TooLong1!"*25})
    assert response.status_code == 401
    assert response.json["msg"] == "Password is invalid"
    
    response = client.post("/register", json={"username": "TooLong"*25, "password": "TooLong1!"})
    assert response.status_code == 401
    assert response.json["msg"] == "Username is invalid"

def test_login_missing_data(client):
    response = client.post("/login", json={})
    assert response.status_code == 400
    assert response.json["msg"] == "Missing username or password"

def test_me_missing_token(client):
    response = client.post("/me", json={})
    assert response.status_code == 400
    assert response.json["msg"] == "Missing token"

def test_me_invalid_token(client):
    response = client.post("/me", json={"jwt_token": "invalid_token"})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid token"

def test_update_info_missing_data(client):
    response = client.post("/update_info", json={})
    assert response.status_code == 400
    assert response.json["msg"] == "Missing token or user data"

def test_update_info_invalid_token(client):
    response = client.post("/update_info", json={"jwt_token": "invalid_token", "user_data": {"email": "test@test.com"}})
    assert response.status_code == 402
    assert response.json["msg"] == "Invalid token"

def test_update_info_invalid_names(client):
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"first_name": "valid_name", "second_name": "TooLong"*25}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid second name"
    
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"second_name": "valid_name", "first_name": "TooLong"*25}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid first name"

def test_update_info_invalid_email(client):
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"email": "invalid_email"}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid email"
    
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"email": ("TooLong"*25) + "@test.com"}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid email"

def test_update_info_invalid_birth_date(client):
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"birth_date": "invalid_birth_date"}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid birth date"
    
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"birth_date": "TooLong"*25}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid birth date"
    
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"birth_date": "10-10-2020"}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid birth date"
    
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"birth_date": "2020-10-40"}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid birth date"
    
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"birth_date": "2020-10-40"}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid birth date"
    
def test_update_info_invalid_phone_number(client):
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"phone_number": "invalid_phone_number"}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid phone number"
    
    response = client.post("/update_info", json={"jwt_token": "valid_token", "user_data": {"phone_number": "+8" + "0"*20}})
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid phone number"
    
# ------====== [VALID CALLS] =====-----

def test_register(client):
    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    assert response.status_code == 201
    assert response.get_json()['msg'] == "User registered successfully!"

    response = client.post('/register', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    assert response.status_code == 402

def test_login(client):
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    assert response.status_code == 401
    assert response.json["msg"] == "Invalid username or password"

    client.post('/register', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    assert response.status_code == 200
    assert 'jwt_token' in response.get_json()

    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'WrongPass1'
    })
    assert response.status_code == 401

def test_me(client):
    client.post('/register', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    token = login_response.get_json()['jwt_token']
    
    response = client.post('/me', json={'jwt_token': token})
    assert response.status_code == 200
    assert response.get_json()['username'] == 'testuser'

def test_update_info(client):
    client.post('/register', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    login_response = client.post('/login', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })
    token = login_response.get_json()['jwt_token']
    
    me_response = client.post('/me', json={'jwt_token': token})
    user_data = me_response.get_json()
    updated_old = user_data['updated_at']
    assert user_data['first_name'] == None
    assert user_data['second_name'] == None
    assert user_data['birth_date'] == None
    assert user_data['email'] == None
    assert user_data['phone_number'] == None
    
    time.sleep(5)
    
    response = client.post('/update_info', json={
        'jwt_token': token,
        'user_data': {
            'first_name': 'John',
            'second_name': 'Doe',
            'birth_date': '2020-10-10',
            'email': 'john.doe@example.com',
            'phone_number': '+88005553535'
        }
    })
    assert response.status_code == 201
    assert response.get_json()['msg'] == 'Successfuly updated user information'

    me_response = client.post('/me', json={'jwt_token': token})
    user_data = me_response.get_json()
    assert user_data['updated_at'] != updated_old
    
    assert user_data['first_name'] == 'John'
    assert user_data['second_name'] == 'Doe'
    assert user_data['birth_date'] == '2020-10-10'
    assert user_data['email'] == 'john.doe@example.com'
    assert user_data['phone_number'] == '+88005553535'
