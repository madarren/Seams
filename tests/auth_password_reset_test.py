'''
Tests for auth_passwordreset_reset_v1.
'''
import pytest
import requests
from src import config

BASE_URL = config.url

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def new_user():
    valid_user = {'email': 'h13badger@gmail.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()


def test_invalid_reset_code(clear, new_user):
    ''' Test InputError raised on invalid reset code. '''
    json_body = {'reset_code': 'h13badger@gmail.com', 'new_password': 'newpass'}
    response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json = json_body)
    assert response.status_code == 400

def test_invalid_password(clear, new_user):
    ''' Test InputError raised on invalid password. '''
    json_body = {'reset_code': '', 'new_password': ''}
    response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json = json_body)
    assert response.status_code == 400

def test_function_runs(clear, new_user):
    ''' Test function runs. '''
    json_body = {'reset_code': '', 'new_password': 'newpass'}
    response = requests.post(f"{BASE_URL}/auth/passwordreset/reset/v1", json = json_body)
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json = {})