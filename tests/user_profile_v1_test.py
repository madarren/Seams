'''
This file contains tests for the implementation of user_profile_v1 and its http wrap.

'''

import pytest
from src.user import user_profile_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v1
import requests
from src import config

BASE_URL = config.url

valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'first', 'name_last': 'last'}
user1_info = {
    'u_id': 1,
    'email': 'valid@email.com',
    'name_first': 'firstname',
    'name_last': 'lastname',
    'handle_str': 'firstnamelastname',
    'profile_img_url': 'static/default.jpg',
}
user2_info = {
    'u_id': 2,
    'email': 'second@email.com',
    'name_first': 'first',
    'name_last': 'last',
    'handle_str': 'firstlast',
    'profile_img_url': 'static/default.jpg',
}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
    clear_v1()

def test_invalid_token_backend(clear):
    ''' Test that the backend implementation raises AccessError for invalid token. '''
    with pytest.raises(AccessError):
        user_profile_v1("token", 1)

def test_invalid_token_frontend(clear):
    ''' Test that the frontend raises AccessError for invalid token. '''
    response = requests.get(f"{BASE_URL}/user/profile/v1?token=token&u_id=1")
    assert response.status_code == 403

def test_invalid_u_id_backend(clear):
    ''' Test that the backend implementation raises InputError for invalid u_id. '''
    token = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')['token']
    with pytest.raises(InputError):
        user_profile_v1(token, 999)

def test_invalid_u_id_frontend(clear):
    ''' Test that the frontend raises InputError for invalid u_id. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    token = response.json()['token']
    response = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id=99")
    assert response.status_code == 400

def test_returns_single_user_backend(clear):
    ''' Test that details of single user is returned in the backend. '''
    reg_return = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    token = reg_return['token']
    u_id = reg_return['auth_user_id']
    user_info = {
        'u_id': 1,
        'email': 'valid@email.com',
        'name_first': 'firstname',
        'name_last': 'lastname',
        'handle_str': 'firstnamelastname',
        'profile_img_url': 'static/default.jpg',
    }
    assert user_profile_v1(token, u_id)['user'] == user_info

def test_returns_single_user_frontend(clear):
    ''' Test that details of single user is returned in the frontend. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    token = response.json()['token']
    u_id = response.json()['auth_user_id']
    response = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={u_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['user'] == user1_info

def test_returns_multiple_users_backend(clear):
    ''' Test that the details of a user with multiple users is returned in the backend. '''
    reg_return = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    token1 = reg_return['token']
    u_id1 = reg_return['auth_user_id']
    reg2_return = auth_register_v1('second@email.com', 'password2', 'first', 'last')
    token2 = reg2_return['token']
    u_id2 = reg2_return['auth_user_id']
    assert user_profile_v1(token1, u_id1)['user'] == user1_info
    assert user_profile_v1(token2, u_id2)['user'] == user2_info
    assert user_profile_v1(token1, u_id2)['user'] == user2_info
    assert user_profile_v1(token2, u_id1)['user'] == user1_info

def test_returns_multiple_users_frontend(clear):
    ''' Test that the details a user with multiple users is returned in the frontend. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    token1 = response.json()['token']
    u_id1 = response.json()['auth_user_id']
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    token2 = response.json()['token']
    u_id2 = response.json()['auth_user_id']
    user_response = requests.get(f"{BASE_URL}/user/profile/v1?token={token1}&u_id={u_id1}")
    assert user_response.status_code == 200
    data = user_response.json()['user']
    user2_response = requests.get(f"{BASE_URL}/user/profile/v1?token={token2}&u_id={u_id2}")
    assert user2_response.status_code == 200
    data2 = user2_response.json()['user']
    user3_response = requests.get(f"{BASE_URL}/user/profile/v1?token={token1}&u_id={u_id2}")
    assert user3_response.status_code == 200
    data3 = user3_response.json()['user']
    user4_response = requests.get(f"{BASE_URL}/user/profile/v1?token={token2}&u_id={u_id1}")
    assert user4_response.status_code == 200
    data4 = user4_response.json()['user']
    assert data == user1_info
    assert data2 == user2_info
    assert data3 == user2_info
    assert data4 == user1_info

requests.delete(f"{BASE_URL}/clear/v1", json = {})
clear_v1()
