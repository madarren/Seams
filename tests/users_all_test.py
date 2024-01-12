'''
This file contains tests for the implementation of users_all_v1 and its http wrap.

'''

import pytest
from src.user import users_all_v1
from src.error import AccessError
from src.other import clear_v1
from src.auth import auth_register_v1
import requests
from src import config

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
        users_all_v1("token")

def test_invalid_token_frontend(clear):
    ''' Test that the frontend raises AccessError for invalid token. '''
    response = requests.get(f"{BASE_URL}/users/all/v1?token=token")
    assert response.status_code == 403

def test_returns_single_user_backend(clear):
    ''' Test that details of single user is returned in the backend. '''
    token = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')['token']
    user_info = {
        'u_id': 1,
        'email': 'valid@email.com',
        'name_first': 'firstname',
        'name_last': 'lastname',
        'handle_str': 'firstnamelastname',
        'profile_img_url': 'static/default.jpg',
    }
    assert users_all_v1(token)['users'] == [user_info]

def test_returns_single_user_frontend(clear):
    ''' Test that details of single user is returned in the frontend. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    token = response.json()['token']
    response = requests.get(f"{BASE_URL}/users/all/v1?token={token}")
    assert response.status_code == 200
    data = response.json()
    user_info = {
        'u_id': 1,
        'email': 'valid@email.com',
        'name_first': 'firstname',
        'name_last': 'lastname',
        'handle_str': 'firstnamelastname',
        'profile_img_url': 'static/default.jpg',
    }
    assert data['users'] == [user_info]

def test_returns_multiple_users_backend(clear):
    ''' Test that details of multiple users is return in the backend. '''
    token1 = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')['token']
    token2 = auth_register_v1('second@email.com', 'password2', 'first', 'last')['token']
    user_list = [
        {
            'u_id': 1,
            'email': 'valid@email.com',
            'name_first': 'firstname',
            'name_last': 'lastname',
            'handle_str': 'firstnamelastname',
            'profile_img_url': 'static/default.jpg',
        },
        {
            'u_id': 2,
            'email': 'second@email.com',
            'name_first': 'first',
            'name_last': 'last',
            'handle_str': 'firstlast',
            'profile_img_url': 'static/default.jpg',
        }
    ]
    assert users_all_v1(token1)['users'] == user_list
    assert users_all_v1(token2)['users'] == user_list

def test_returns_multiple_users_frontend(clear):
    ''' Test that details of multiple users is return in the frontend. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    token1 = response.json()['token']
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    token2 = response.json()['token']
    user_response = requests.get(f"{BASE_URL}/users/all/v1?token={token1}")
    assert user_response.status_code == 200
    data = user_response.json()
    user2_response = requests.get(f"{BASE_URL}/users/all/v1?token={token2}")
    assert user2_response.status_code == 200
    data2 = user2_response.json()
    user_list = [
        {
            'u_id': 1,
            'email': 'valid@email.com',
            'name_first': 'firstname',
            'name_last': 'lastname',
            'handle_str': 'firstnamelastname',
            'profile_img_url': 'static/default.jpg',
        },
        {
            'u_id': 2,
            'email': 'second@email.com',
            'name_first': 'first',
            'name_last': 'last',
            'handle_str': 'firstlast',
            'profile_img_url': 'static/default.jpg',
        }
    ]
    assert data['users'] == user_list
    assert data2['users'] == user_list
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
    clear_v1()
