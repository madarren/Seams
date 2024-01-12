"""
Tests for dm/list/v1
"""
import pytest
import requests

from src.error import AccessError
from src import config

BASE_URL = config.url
valid_user_1 = {'email': 'valid1@email.com', 'password': 'password', 'name_first': 'valid1', 'name_last': 'lastname'}
valid_user_2 = {'email': 'valid2@email.com', 'password': 'password', 'name_first': 'valid2', 'name_last': 'lastname'}
valid_user_3 = {'email': 'valid3@email.com', 'password': 'password', 'name_first': 'valid3', 'name_last': 'lastname'}
valid_user_4 = {'email': 'valid4@email.com', 'password': 'password', 'name_first': 'valid4', 'name_last': 'lastname'}
valid_user_5 = {'email': 'valid5@email.com', 'password': 'password', 'name_first': 'valid5', 'name_last': 'lastname'}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

def test_invalid_token(clear):
    ''' Tests if token is valid.'''
    token = 'ahjsbfkha'
    response = requests.get(f"{BASE_URL}/dm/list/v1?token={token}")

    assert response.status_code == 403

def test_user_not_in_dms(clear):
    ''' Tests if the user is in dms.'''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_1)
    assert response.status_code == 200
    response_data = response.json()
    token = response_data['token']
    dms_response = requests.get(f"{BASE_URL}/dm/list/v1?token={token}")
    assert dms_response.status_code == 200
    dms_response_data = dms_response.json()
    assert dms_response_data['dms'] == []

def test_user_in_single_dm(clear):
    ''' Tests if the user is in single dm.'''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_1)
    assert response.status_code == 200
    response_data = response.json()
    token = response_data['token']
    response_1 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_2)
    assert response_1.status_code == 200
    response_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_3)
    assert response_2.status_code == 200

    response_1_data = response_1.json()
    response_2_data = response_2.json()
    u_id_1 = response_1_data['auth_user_id']
    u_id_2 = response_2_data['auth_user_id']
    u_ids = []
    u_ids.append(u_id_1)
    u_ids.append(u_id_2)

    dms_create_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token,
        'u_ids': u_ids,
    })
    assert dms_create_response.status_code == 200
    dms_create_data = dms_create_response.json()
    dms_id = dms_create_data['dm_id']
    dms_list_response = requests.get(f"{BASE_URL}/dm/list/v1?token={token}")
    assert dms_list_response.status_code == 200
    dms_list_data = dms_list_response.json()
    dms_dict = {'dms': [{'dm_id': dms_id, 'name': 'valid1lastname, valid2lastname, valid3lastname'}]}
    assert dms_list_data == dms_dict

def test_user_in_multiple_dms(clear):
    ''' Tests if the user is in multiple dms.'''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_1)
    assert response.status_code == 200
    response_data = response.json()
    token = response_data['token']
    u_id = response_data['auth_user_id']
    response_1 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_2)
    assert response_1.status_code == 200
    response_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_3)
    assert response_2.status_code == 200

    response_1_data = response_1.json()
    response_2_data = response_2.json()
    u_id_1 = response_1_data['auth_user_id']
    u_id_2 = response_2_data['auth_user_id']

    response_3 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_4)
    assert response_3.status_code == 200
    response_4 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_5)
    assert response_4.status_code == 200
    response_3_data = response_3.json()
    response_4_data = response_4.json()

    token_1 = response_3_data['token']
    u_id_3 = response_3_data['auth_user_id']
    u_id_4 = response_4_data['auth_user_id']

    u_ids = []
    u_ids.append(u_id_1)
    u_ids.append(u_id_2)

    u_ids_1 = []
    u_ids_1.append(u_id)

    u_ids_2 = []
    u_ids_2.append(u_id_3)
    u_ids_2.append(u_id_4)

    dms_create_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token,
        'u_ids': u_ids
        })

    assert dms_create_response.status_code == 200    
    dms_create_data = dms_create_response.json()
    dms_id = dms_create_data['dm_id']
    dms_create_response_1 = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token_1,
        'u_ids': u_ids_1
        })

    assert dms_create_response_1.status_code == 200
    dms_create_data_1 = dms_create_response_1.json()
    dms_id_1 = dms_create_data_1['dm_id']
    dms_create_response_2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token,
        'u_ids': u_ids_2
        })

    assert dms_create_response.status_code == 200
    dms_create_data_2 = dms_create_response_2.json()
    dms_id_2 = dms_create_data_2['dm_id']

    dms_list_response = requests.get(f"{BASE_URL}/dm/list/v1?token={token}")
    assert dms_list_response.status_code == 200
    dms_list_data = dms_list_response.json()

    dms_dict = []
    dms_dict_1 = {'dm_id': dms_id, 'name': 'valid1lastname, valid2lastname, valid3lastname'}
    dms_dict_2 = {'dm_id': dms_id_1, 'name': 'valid1lastname, valid4lastname'}
    dms_dict_3 = {'dm_id': dms_id_2, 'name': 'valid1lastname, valid4lastname, valid5lastname'}
    dms_dict.append(dms_dict_1)
    dms_dict.append(dms_dict_2)
    dms_dict.append(dms_dict_3)

    assert dms_list_data == {'dms': dms_dict}

requests.delete(f"{BASE_URL}/clear/v1", json = {})
