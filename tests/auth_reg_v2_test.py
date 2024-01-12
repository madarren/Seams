'''
Tests for auth/register/v2. i.e. http wrap of auth_register from iteration 1.
Note: do not need to test for handles and global permission as these are in the original tests.

'''

import pytest
import requests
from src import config
from src.tokens import *

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid_user2 = {'email': 'second@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
long_name = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz'

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

def test_invalid_email(clear):
    ''' Test invalid email raises InputError. '''
    json_data = {'email': 'invalidemail', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = json_data)
    assert response.status_code == 400

def test_can_create_one_user(clear):
    ''' Test a valid user can be registered. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert response.status_code == 200
    response_data = response.json()
    payload = {
        'auth_user_id': 1,
        'session_id': 1
    }
    assert payload == decode_token(response_data['token'])
    assert response_data['auth_user_id'] == 1

def test_duplicate_email(clear):
    ''' Test duplicate email raises InputError. '''
    json_data = {'email': 'valid@email.com', 'password': 'password1', 'name_first': 'first', 'name_last': 'last'}
    requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = json_data)
    assert response.status_code == 400

def test_invalid_password(clear):
    ''' Test an invalid password raises InputError. '''
    json_data = {'email': 'valid@email.com', 'password': 'inval', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = json_data)
    assert response.status_code == 400

def test_first_name_too_short(clear):
    ''' Test short first name raises InputError. '''
    json_data = {'email': 'valid@email.com', 'password': 'password', 'name_first': '', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = json_data)
    assert response.status_code == 400

def test_first_name_too_long(clear):
    ''' Test long first name raises InputError. '''
    json_data = {'email': 'valid@email.com', 'password': 'password', 'name_first': long_name , 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = json_data)
    assert response.status_code == 400

def test_last_name_too_short(clear):
    ''' Test short last name raises InputError. '''
    json_data = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': ''}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = json_data)
    assert response.status_code == 400

def test_last_name_too_long(clear):
    ''' Test long last name raises InputError. '''
    json_data = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': long_name}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = json_data)
    assert response.status_code == 400

def test_multiple_create(clear):
    ''' Test that multiple registers return correct token and id for second user. '''
    requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    response_second = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user2)
    assert response_second.status_code == 200
    response_second_data = response_second.json()
    payload = {
        'auth_user_id': 2,
        'session_id': 2
    }
    assert decode_token(response_second_data['token']) == payload
    assert response_second_data['auth_user_id'] == 2

requests.delete(f"{BASE_URL}/clear/v1", json = {})
