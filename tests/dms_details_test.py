"""
Tests for dm/list/v1
"""
import pytest
import requests

from src.error import AccessError, InputError
from src import config

BASE_URL = config.url
valid_user_1 = {'email': 'valid1@email.com', 'password': 'password', 'name_first': 'valid1', 'name_last': 'lastname'}
valid_user_2 = {'email': 'valid2@email.com', 'password': 'password', 'name_first': 'valid2', 'name_last': 'lastname'}
valid_user_3 = {'email': 'valid3@email.com', 'password': 'password', 'name_first': 'valid3', 'name_last': 'lastname'}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def user_1():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_1)
    assert response.status_code == 200
    return response.json()

def test_no_valid_ids(clear):
    ''' Tests if token is valid.'''
    token = 'afasf'
    dm_id = -1
    response = requests.get(f"{BASE_URL}/dm/details/v1?token={token}&dm_id={dm_id}")
    assert response.status_code == 403

def test_invalid_dm_id(clear, user_1):
    ''' Tests if dm_id is valid.'''
    token = user_1['token']
    dm_id = -1
    response = requests.get(f"{BASE_URL}/dm/details/v1?token={token}&dm_id={dm_id}")
    assert response.status_code == 400

def test_user_not_in_dm(clear, user_1):
    ''' Tests if user is dm.'''
    token = user_1['token']
    response_1 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_2)
    assert response_1.status_code == 200
    response_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_3)
    assert response_2.status_code == 200

    response_1_data = response_1.json()
    response_2_data = response_2.json()
    token_1 = response_1_data['token']
    u_id_2 = response_2_data['auth_user_id']
    u_ids_list_2 = []
    u_ids_list_2.append(u_id_2)

    dms_create_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token_1, 
        'u_ids': u_ids_list_2,
        })
    assert dms_create_response.status_code == 200
    dms_create_data = dms_create_response.json()
    dm_id = dms_create_data['dm_id']

    response = requests.get(f"{BASE_URL}/dm/details/v1?token={token}&dm_id={dm_id}")
    assert response.status_code == 403

def test_dms_details_works(clear, user_1):
    ''' Tests if dm details works.'''
    token = user_1['token']
    u_id = user_1['auth_user_id']
    response_1 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_2)
    assert response_1.status_code == 200
    response_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_3)
    assert response_2.status_code == 200

    response_1_data = response_1.json()
    response_2_data = response_2.json()
    token_1 = response_1_data['token']
    token_2 = response_2_data['token']
    u_id_1 = response_1_data['auth_user_id']
    u_id_2 = response_2_data['auth_user_id']
    u_ids_list = []
    u_ids_list.append(u_id_1)
    u_ids_list.append(u_id_2)

    dms_create_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token,
        'u_ids': u_ids_list,
        })
    assert dms_create_response.status_code == 200
    dms_create_data = dms_create_response.json()
    dm_id = dms_create_data['dm_id']

    user_resp_1 = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={u_id}")
    assert user_resp_1.status_code == 200
    user_details_1 = user_resp_1.json()

    user_resp_2 = requests.get(f"{BASE_URL}/user/profile/v1?token={token_1}&u_id={u_id_1}")
    assert user_resp_2.status_code == 200
    user_details_2 = user_resp_2.json()

    user_resp_3 = requests.get(f"{BASE_URL}/user/profile/v1?token={token_2}&u_id={u_id_2}")
    assert user_resp_3.status_code == 200
    user_details_3 = user_resp_3.json()

    members = []
    members.append(user_details_1['user'])
    members.append(user_details_2['user'])
    members.append(user_details_3['user'])

    dms_detail_response = requests.get(f"{BASE_URL}/dm/details/v1?token={token}&dm_id={dm_id}")

    assert dms_detail_response.status_code == 200

    dms_detail_response_data = dms_detail_response.json()
    assert dms_detail_response_data['name'] == 'valid1lastname, valid2lastname, valid3lastname'
    assert len(dms_detail_response_data['members']) == 3
    assert dms_detail_response_data['members'][0]['u_id'] == members[0]['u_id']
    assert dms_detail_response_data['members'][1]['u_id'] == members[1]['u_id']
    assert dms_detail_response_data['members'][2]['u_id'] == members[2]['u_id']
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
