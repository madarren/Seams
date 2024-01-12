'''
This file contains tests for the implementation of user_setemail_v1 and its http wrap.
'''

import pytest
from src.user import user_setemail_v1, user_profile_v1
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
        user_setemail_v1("token", "new@email.com")

def test_invalid_token_frontend(clear):
    ''' Test that the frontend raises AccessError for invalid token. '''
    json_data = {'token': 'token', 'email': 'new@email.com'}
    response = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = json_data)
    assert response.status_code == 403

def test_invalid_email_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the email is invalid. '''
    with pytest.raises(InputError):
        user_setemail_v1(new_user_backend['token'], 'invalidemail')

def test_duplicate_email_backend(clear, new_user_backend):
    ''' Test that the backend raises InputError when the email is a duplicate. '''
    auth_register_v1('second@email.com', 'password', 'firstname', 'lastname')
    with pytest.raises(InputError):
        user_setemail_v1(new_user_backend['token'], 'second@email.com')

def test_invalid_email_frontend(clear, new_user_frontend):
    ''' Test that the frontend raises InputError when the email is invalid or duplicate. '''
    json_inval = {'token': new_user_frontend['token'], 'email': 'invalidemail'}
    inval_resp = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = json_inval)
    assert inval_resp.status_code == 400
    requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    json_dup = {'token': new_user_frontend['token'], 'email': 'second@email.com'}
    dup_resp = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = json_dup)
    assert dup_resp.status_code == 400

def test_original_email_backend(clear, new_user_backend):
    ''' Test that the backend works when the email is the same as the original. '''
    token, auth_user_id = new_user_backend['token'], new_user_backend['auth_user_id']
    user_setemail_v1(new_user_backend['token'], 'valid@email.com')
    assert user_profile_v1(token, auth_user_id)['user']['email'] == 'valid@email.com'

def test_original_email_frontend(clear, new_user_frontend):
    ''' Test the email is 'changed' when the same email as before is input for frontend. '''
    json_orig = {'token': new_user_frontend['token'], 'email': 'valid@email.com'}
    orig_resp = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = json_orig)
    assert orig_resp.status_code == 200

def test_single_user_email_change_backend(clear, new_user_backend):
    ''' Test that backend can change user's email when there is just one user. '''
    token, auth_user_id = new_user_backend['token'], new_user_backend['auth_user_id']
    user_setemail_v1(new_user_backend['token'], 'new@email.com')
    assert user_profile_v1(token, auth_user_id)['user']['email'] == 'new@email.com'

def test_single_user_email_change_frontend(clear, new_user_frontend):
    ''' Test that frontend can change user's email when there is just one user. '''
    token, auth_user_id = new_user_frontend['token'], new_user_frontend['auth_user_id']
    json_data = {'token': token, 'email': 'new@email.com'}
    response = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = json_data)
    assert response.status_code == 200
    check_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={auth_user_id}")
    check_data = check_resp.json()
    assert check_data['user']['email'] == 'new@email.com'

def test_multi_user_email_change_backend(clear, new_user_backend):
    ''' Test that the backend can change a user's email when there is more than one user. '''
    reg_return = auth_register_v1('second@email.com', 'password', 'mori', 'calliope')
    token2, auth_user_id2 = reg_return['token'], reg_return['auth_user_id']
    user_setemail_v1(token2, 'new@email.com')
    assert user_profile_v1(token2, auth_user_id2)['user']['email'] == 'new@email.com'
    with pytest.raises(InputError):
        user_setemail_v1(new_user_backend['token'], 'new@email.com')

def test_mutli_user_email_change_frontend(clear, new_user_frontend):
    ''' Test that frontend can change a user's email when there is more than one user. '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    token, auth_user_id = response.json()['token'], response.json()['auth_user_id']
    json_data = {'token': token, 'email': 'new@email.com'}
    response = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = json_data)
    assert response.status_code == 200
    check_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={auth_user_id}")
    check_data = check_resp.json()
    assert check_data['user']['email'] == 'new@email.com'
    json_dup = {'token': new_user_frontend['token'], 'email': 'new@email.com'}
    dep_resp = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = json_dup)
    assert dep_resp.status_code == 400

requests.delete(f"{BASE_URL}/clear/v1", json = {})
clear_v1()
