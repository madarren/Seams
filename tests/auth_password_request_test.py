'''
Tests for auth_passwordreset_request_v1.
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


def test_function_runs(clear, new_user):
    ''' Test function runs. '''
    json_body = {'email': 'h13badger@gmail.com'}
    response = requests.post(f"{BASE_URL}/auth/passwordreset/request/v1", json = json_body)
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
