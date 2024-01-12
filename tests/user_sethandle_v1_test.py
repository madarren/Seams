'''
This file contains tests for the implementation of user_sethandle_v1 and its http wrap.
'''

import pytest
from src.user import user_sethandle_v1, user_profile_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v1
import requests
from src import config

BASE_URL = config.url
valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'joel', 'name_last': 'embiid'}

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
        user_sethandle_v1("token", "newhandle")

def test_invalid_token_frontend(clear):
    ''' Test that the frontend raises AccessError for invalid token. '''
    json_data = {'token': 'token', 'handle_str': 'newhandle'}
    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_data)
    assert response.status_code == 403

def test_short_handle_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the handle is too short. '''
    with pytest.raises(InputError):
        user_sethandle_v1(new_user_backend['token'], '12')

def test_long_handle_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the handle is too long. '''
    with pytest.raises(InputError):
        user_sethandle_v1(new_user_backend['token'], 'istwentyonecharacters')

def test_invalid_handle_length_frontend(clear, new_user_frontend):
    ''' Test that the frontend raises InputError when the handle length is invalid. '''
    json_short = {'token': new_user_frontend['token'], 'handle_str': '12'}
    short_resp = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_short)
    assert short_resp.status_code == 400
    json_long = {'token': new_user_frontend['token'], 'handle_str': 'istwentyonecharacters'}
    long_resp = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_long)
    assert long_resp.status_code == 400

def test_non_alphanumeric_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the handle is non alphanumeric. '''
    with pytest.raises(InputError):
        user_sethandle_v1(new_user_backend['token'], '12345!!_?')

def test_non_lowercase_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the handle is non lowercase. '''
    with pytest.raises(InputError):
        user_sethandle_v1(new_user_backend['token'], 'someCHARACTERS')

def test_nonalphanumeric_lowercase_frontend(clear, new_user_frontend):
    ''' Test that the frontend raises InputError when the handle is not lowercase alphanumeric. '''
    json_alpha = {'token': new_user_frontend['token'], 'handle_str': '12345!!'}
    short_resp = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_alpha)
    assert short_resp.status_code == 400
    json_lower = {'token': new_user_frontend['token'], 'handle_str': 'someCHAR'}
    lower_resp = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_lower)
    assert lower_resp.status_code == 400

def test_duplicate_handle_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the handle is used by another user. '''
    auth_register_v1('second@email.com', 'password', 'first', 'last')
    with pytest.raises(InputError):
        user_sethandle_v1(new_user_backend['token'], 'firstlast')

def test_invalid_handle_frontend(clear, new_user_frontend):
    ''' Test that the frontend raises InputError when the handle is used by another user. '''
    requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    json_dup = {'token': new_user_frontend['token'], 'handle_str': 'joelembiid'}
    dup_resp = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_dup)
    assert dup_resp.status_code == 400

def test_original_handle_backend(clear, new_user_backend):
    ''' Test that the backend works when the handle is the same as the original. '''
    token, auth_user_id = new_user_backend['token'], new_user_backend['auth_user_id']
    user_sethandle_v1(new_user_backend['token'], 'firstnamelastname')
    assert user_profile_v1(token, auth_user_id)['user']['handle_str'] == 'firstnamelastname'

def test_original_handle_frontend(clear, new_user_frontend):
    ''' Test the handle is 'changed' when the same handle as before is input for frontend. '''
    json_orig = {'token': new_user_frontend['token'], 'handle_str': 'firstnamelastname'}
    orig_resp = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_orig)
    assert orig_resp.status_code == 200

def test_single_user_handle_change_backend(clear, new_user_backend):
    ''' Test that backend can change user's handle when there is just one user. '''
    token, auth_user_id = new_user_backend['token'], new_user_backend['auth_user_id']
    user_sethandle_v1(new_user_backend['token'], 'newhandle')
    assert user_profile_v1(token, auth_user_id)['user']['handle_str'] == 'newhandle'

def test_single_user_handle_change_frontend(clear, new_user_frontend):
    ''' Test that frontend can change user's handle when there is just one user. '''
    token, auth_user_id = new_user_frontend['token'], new_user_frontend['auth_user_id']
    json_data = {'token': token, 'handle_str': 'newhandle'}
    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_data)
    assert response.status_code == 200
    check_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={auth_user_id}")
    check_data = check_resp.json()
    assert check_data['user']['handle_str'] == 'newhandle'

def test_multi_user_handle_change_backend(clear, new_user_backend):
    ''' Test that the backend can change a user's handle when there is more than one user. '''
    reg_return = auth_register_v1('second@email.com', 'password', 'mori', 'calliope')
    token2, auth_user_id2 = reg_return['token'], reg_return['auth_user_id']
    user_sethandle_v1(token2, 'newhandle')
    assert user_profile_v1(token2, auth_user_id2)['user']['handle_str'] == 'newhandle'
    with pytest.raises(InputError):
        user_sethandle_v1(new_user_backend['token'], 'newhandle')

def test_mutli_user_handle_change_frontend(clear, new_user_frontend):
    ''' Test that frontend can change a user's handle when there is more than one user. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    token, auth_user_id = response.json()['token'], response.json()['auth_user_id']
    json_data = {'token': token, 'handle_str': 'newhandle'}
    response = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_data)
    assert response.status_code == 200
    check_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={auth_user_id}")
    check_data = check_resp.json()
    assert check_data['user']['handle_str'] == 'newhandle'
    json_dup = {'token': new_user_frontend['token'], 'handle_str': 'newhandle'}
    dep_resp = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_dup)
    assert dep_resp.status_code == 400

requests.delete(f"{BASE_URL}/clear/v1", json = {})
clear_v1()
