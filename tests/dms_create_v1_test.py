"""
Tests for dm/create/v1
"""
from src import config
import pytest
import requests

BASE_URL = config.url
valid_user_1 = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'Bob', 'name_last': 'lastname'}
valid_user_2 = {'email': 'valid1@email.com', 'password': 'password', 'name_first': 'John', 'name_last': 'lastname'}
valid_user_3 = {'email': 'valid2@email.com', 'password': 'password', 'name_first': 'Steve', 'name_last': 'lastname'}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def user_reg_1():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_1)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def user_reg_2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_2)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def user_reg_3():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_3)
    assert response.status_code == 200
    return response.json()


def test_valid_dm(clear, user_reg_1, user_reg_2, user_reg_3):
    """
    Tests creating a valid dm.
    """
    token = user_reg_1['token']
    u_ids = []
    u_id_1 = user_reg_2['auth_user_id']
    u_id_2 = user_reg_3['auth_user_id']
    u_ids.append(u_id_1)
    u_ids.append(u_id_2)

    dm_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": token, 
        "u_ids": u_ids
    })
    assert dm_response.status_code == 200
    payload = dm_response.json()
    assert payload["dm_id"] == 0

def test_dm_create_invalid_user_id(clear, user_reg_1, user_reg_2):
    ''' Tests an invalid user id. '''

    token = user_reg_1['token']
    u_ids = []
    u_id_1 = user_reg_2['auth_user_id']
    u_id_2 = -1
    u_ids.append(u_id_1)
    u_ids.append(u_id_2)

    dm_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": token, 
        "u_ids": u_ids,
    })
    assert dm_response.status_code == 400

def test_dm_create_unauthorised_token(clear, user_reg_2, user_reg_3):
    ''' Tests for invalid user '''
    token = 'dfsdf'
    u_ids = []
    u_id_1 = user_reg_2['auth_user_id']
    u_id_2 = user_reg_3['auth_user_id']
    u_ids.append(u_id_1)
    u_ids.append(u_id_2)

    dm_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": token, 
        "u_ids": u_ids
    })
    assert dm_response.status_code == 403

def test_dm_create_duplicate_id(clear, user_reg_1, user_reg_2, user_reg_3):
    token = user_reg_1['token']
    u_ids = []
    u_id_1 = user_reg_2['auth_user_id']
    u_id_2 = user_reg_2['auth_user_id']
    u_ids.append(u_id_1)
    u_ids.append(u_id_2)

    dm_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": token, 
        "u_ids": u_ids
    })

    assert dm_response.status_code == 400
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
