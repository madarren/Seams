"""
Tests for dm/remove/v1
"""
import pytest
import requests
from src.tokens import *
from src.other import check_valid_token, check_valid_dm_id
from src import config
from src.dms import *

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid_user2 = {"email": "valid2@email.com", "password": "123456", "name_first": "autumn", "name_last": "barnes"}
valid_user3 = {"email": "valid3@email.com", "password": "abcdef", "name_first": "jane", "name_last": "doe"}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def user_reg_1():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()

@pytest.fixture
def user_reg_2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user2)
    return response.json()

@pytest.fixture
def user_reg_3():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user3)
    return response.json()


def test_remove_valid_dm_success(clear, user_reg_1, user_reg_2):
    ''' Tests removing a valid dm '''
    new_token = user_reg_1['token']
    u_id = user_reg_2['auth_user_id']
    u_ids = []
    u_ids.append(u_id)
    response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": new_token,
        "u_ids": u_ids
    })
    assert response.status_code == 200
    dm_id = response.json()['dm_id']
    assert dm_id == 0
   
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
        "token": new_token,
        "dm_id": dm_id
    })
    assert response.status_code == 200

def test_dm_remove_invalid_dm(clear, user_reg_1, user_reg_2):
    ''' If the DM has an invalid id gives InputError '''
    bad_dm = 999
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
        "token": user_reg_1['token'],
        "dm_id": bad_dm
    })
    assert response.status_code == 400

def test_dm_remove_not_dm_creator(clear, user_reg_1, user_reg_2):
    ''' Gives AccessError if given valid DM but user is not the creator. '''
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": user_reg_1['token'], 
        "u_ids": [user_reg_2['auth_user_id']]
    }).json()["dm_id"]

    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {"token": user_reg_2['token'], "dm_id": dm_id})
    assert response.status_code == 403

def test_dm_remove_token_invalid(clear, user_reg_1, user_reg_2):
    ''' Gives AccessError if the token is invalid '''
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": user_reg_1['token'],
        "u_ids": [user_reg_2['auth_user_id']]
    }).json()["dm_id"]

    bad_token = '999'
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
        "token": bad_token,
        "dm_id": dm_id
    })
    assert response.status_code == 403

def test_dm_remove_user_not_in(clear, user_reg_1, user_reg_2):
    ''' Gives Access Error when the DM is valid and the user is no longer in DM '''
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = {
    "token": user_reg_1['token'],
    "u_ids": [user_reg_2['auth_user_id']]
    }).json()["dm_id"]

    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
    "token": ' ',
    "dm_id": dm_id
    })
    assert response.status_code == 403

def test_dm_remove_owner_nonmember_cannot_remove(clear, user_reg_1, user_reg_2, user_reg_3):
    ''' Give AccessError if owner tries to remove the dm after leaving and is now a nonmember '''
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = {
    "token": user_reg_1['token'],
    "u_ids": [user_reg_2['auth_user_id']]
    }).json()["dm_id"]

    json_data = {'token': user_reg_1['token'], 'dm_id': dm_id}
    owner_leave = requests.post(f"{BASE_URL}/dm/leave/v1", json = json_data)
    owner_leave = user_reg_1
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
    "token": owner_leave,
    "dm_id": dm_id
    })
    assert response.status_code == 403

requests.delete(f"{BASE_URL}/clear/v1", json = {})
