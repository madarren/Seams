'''
This file contains tests for the implementation of auth_logout_v1 and its http wrap.

'''
import pytest
from src.auth import auth_logout_v1
from src.error import AccessError
from src.other import clear_v1
import requests
from src import config
from src.tokens import *

BASE_URL = config.url

valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'first', 'name_last': 'last'}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
    clear_v1()

def test_invalid_token_backend(clear):
    ''' Test that the backend implementation still raises AccessError for invalid token. '''
    with pytest.raises(AccessError):
        auth_logout_v1("token")

def test_invalid_token_frontend(clear):
    ''' Test that the frontend raises AccessError for invalid token. '''
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': 'token'})
    assert response.status_code == 403

def test_remove_valid_token_single_user_backend(clear):
    ''' Test that a single token can be removed from the backend. '''
    token = generate_token(1)
    assert auth_logout_v1(token) == {}
    with pytest.raises(AccessError):
        auth_logout_v1(token)

def test_remove_valid_token_single_user_frontend(clear):
    ''' Test that a single token can be removed from the frontend. '''
    new_user_response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    token = new_user_response.json()['token']
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': token})
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': token})
    assert response.status_code == 403

def test_remove_valid_token_second_user_backend(clear):
    ''' Test that the second token can be removed with multiple tokens in the backend. '''
    generate_token(1)
    token2 = generate_token(2)
    token3 = generate_token(3)
    assert auth_logout_v1(token2) == {}
    assert auth_logout_v1(token3) == {}
    with pytest.raises(AccessError):
        auth_logout_v1(token2)

def test_remove_valid_token_second_user_frontend(clear):
    ''' Test that the second token can be removed with multiple tokens in the frontend. '''
    requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    second_response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    token = second_response.json()['token']
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': token})
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json = {'token': token})
    assert response.status_code == 403

requests.delete(f"{BASE_URL}/clear/v1", json = {})
clear_v1()
