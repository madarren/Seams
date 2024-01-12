'''
This file contains tests for the implementation of user_setname_v1 and its http wrap.

'''

import pytest
from src.user import user_setname_v1, user_profile_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v1
import requests
from src import config

BASE_URL = config.url

valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'joel', 'name_last': 'embiid'}
long_name = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz'

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
    clear_v1()

@pytest.fixture
def new_user_backend():
    return auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')

@pytest.fixture
def new_user_frontend():
    valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()


def test_invalid_token_backend(clear):
    ''' Test that the backend implementation raises AccessError for invalid token. '''
    with pytest.raises(AccessError):
        user_setname_v1("token", "firstname", "lastname")

def test_invalid_token_frontend(clear):
    ''' Test that the frontend raises AccessError for invalid token. '''
    json_data = {'token': 'token', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json = json_data)
    assert response.status_code == 403

def test_short_first_name_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the first name is too short. '''
    with pytest.raises(InputError):
        user_setname_v1(new_user_backend['token'], "", "lastname")

def test_long_first_name_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the first name is too long. '''
    with pytest.raises(InputError):
        user_setname_v1(new_user_backend['token'], long_name, "lastname")

def test_invalid_first_name_frontend(clear, new_user_frontend):
    ''' Test that the frontend raises InputError when the first name is invalid. '''
    json_short = {'token': new_user_frontend['token'], 'name_first': '', 'name_last': 'last'}
    short_resp = requests.put(f"{BASE_URL}/user/profile/setname/v1", json = json_short)
    assert short_resp.status_code == 400
    json_long = {'token': new_user_frontend['token'], 'name_first': long_name, 'name_last': 'last'}
    long_resp = requests.put(f"{BASE_URL}/user/profile/setname/v1", json = json_long)
    assert long_resp.status_code == 400

def test_short_last_name_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the last name is too short. '''
    with pytest.raises(InputError):
        user_setname_v1(new_user_backend['token'], "first", "")

def test_long_last_name_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the last name is too long. '''
    with pytest.raises(InputError):
        user_setname_v1(new_user_backend['token'], "first", long_name)

def test_invalid_last_name_frontend(clear, new_user_frontend):
    ''' Test that the frontend raises InputError when the last name is invalid. '''
    json_short = {'token': new_user_frontend['token'], 'name_first': 'first', 'name_last': ''}
    short_resp = requests.put(f"{BASE_URL}/user/profile/setname/v1", json = json_short)
    assert short_resp.status_code == 400
    json_long = {'token': new_user_frontend['token'], 'name_first': 'first', 'name_last': long_name}
    long_resp = requests.put(f"{BASE_URL}/user/profile/setname/v1", json = json_long)
    assert long_resp.status_code == 400

def test_single_user_name_change_backend(clear, new_user_backend):
    ''' Test that backend can change user's names when there is just one user. '''
    token, auth_user_id = new_user_backend['token'], new_user_backend['auth_user_id']
    user_setname_v1(new_user_backend['token'], 'first', 'last')
    assert user_profile_v1(token, auth_user_id)['user']['name_first'] == 'first'
    assert user_profile_v1(token, auth_user_id)['user']['name_last'] == 'last'

def test_single_user_name_change_frontend(clear, new_user_frontend):
    ''' Test that frontend can change user's names when there is just one user. '''
    token, auth_user_id = new_user_frontend['token'], new_user_frontend['auth_user_id']
    json_data = {'token': token, 'name_first': 'first', 'name_last': 'last'}
    response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json = json_data)
    assert response.status_code == 200
    check_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={auth_user_id}")
    check_data = check_resp.json()
    assert check_data['user']['name_first'] == 'first'
    assert check_data['user']['name_last'] == 'last'

def test_multi_user_name_change_backend(clear, new_user_backend):
    ''' Test that the backend can change a user's names when there is more than one user. '''
    reg_return = auth_register_v1('second@email.com', 'password', 'mori', 'calliope')
    token2, auth_user_id2 = reg_return['token'], reg_return['auth_user_id']
    user_setname_v1(token2, 'amelia', 'watson')
    assert user_profile_v1(token2, auth_user_id2)['user']['name_first'] == 'amelia'
    assert user_profile_v1(token2, auth_user_id2)['user']['name_last'] == 'watson'

def test_mutli_user_name_change_frontend(clear, new_user_frontend):
    ''' Test that frontend can change a user's names when there is more than one user. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    token, auth_user_id = response.json()['token'], response.json()['auth_user_id']
    json_data = {'token': token, 'name_first': 'tyrese', 'name_last': 'maxey'}
    response = requests.put(f"{BASE_URL}/user/profile/setname/v1", json = json_data)
    assert response.status_code == 200
    check_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={auth_user_id}")
    check_data = check_resp.json()
    assert check_data['user']['name_first'] == 'tyrese'
    assert check_data['user']['name_last'] == 'maxey'

requests.delete(f"{BASE_URL}/clear/v1", json = {})
clear_v1()
