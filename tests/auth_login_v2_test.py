'''
Tests for auth/login/v2. i.e. http wrap of auth_login from iteration 1.

'''

import pytest
import requests
from src import config
from src.tokens import *

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid_login = {"email": "valid@email.com", "password": "password"}

another_valid_user = {"email": "anothervalid@email.com", "password": "anotherpassword", "name_first": "firstname", "name_last": "lastname"}
another_valid_login = {"email": "anothervalid@email.com", "password": "anotherpassword"}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})


def test_no_registered_users(clear):
    '''
    No registered users yet
    Note: email is valid 
    '''
    response = requests.post(f"{BASE_URL}/auth/login/v2", json = valid_login)
    assert response.status_code == 400


def test_wrong_registered_email(clear):
    ''' Login with a valid email that is not yet registered. Data store does contain an email '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert response.status_code == 200

    response = requests.post(f"{BASE_URL}/auth/login/v2", json = another_valid_login)
    assert response.status_code == 400

def test_successful_login(clear):
    ''' test successful login '''
    reg_response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    login_response = requests.post(f"{BASE_URL}/auth/login/v2", json = valid_login)
    assert login_response.status_code == 200

    reg_data = reg_response.json()
    login_data = login_response.json()
    assert reg_data["auth_user_id"] == login_data['auth_user_id']
    assert reg_data["token"] != login_data["token"]

def test_incorrect_password(clear):
    ''' email used to login matches one in database, but password is incorrect '''
    requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)

    json_data = {"email": "valid@email.com", "password": "incorrectpassword"}
    response = requests.post(f"{BASE_URL}/auth/login/v2", json = json_data)
    assert response.status_code == 400

def test_multiple_successful_login(clear):
    ''' Testing when multiple users login '''
    reg_data_1 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user).json()
    reg_data_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user).json()

    response_1 = requests.post(f"{BASE_URL}/auth/login/v2", json = valid_login)
    response_2 = requests.post(f"{BASE_URL}/auth/login/v2", json = another_valid_login)

    assert response_1.status_code == 200
    assert response_2.status_code == 200

    login_data_1 = response_1.json()
    login_data_2 = response_2.json()

    assert reg_data_1['auth_user_id'] == login_data_1['auth_user_id']
    assert reg_data_2['auth_user_id'] == login_data_2['auth_user_id']

    assert reg_data_1["token"] != login_data_1["token"]
    assert reg_data_2["token"] != login_data_2["token"]

requests.delete(f"{BASE_URL}/clear/v1", json = {})
