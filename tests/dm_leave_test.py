"""
Tests for dm/leave/v1.
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


def test_no_valid_ids(clear):
    ''' Test AccessError is raised when token is invalid. '''
    json_data = {'token': 'token', 'dm_id': 1}
    response = requests.post(f"{BASE_URL}/dm/leave/v1", json = json_data)
    assert response.status_code == 403

def test_invalid_dm_id(clear, user_reg_1):
    json_data = {'token': user_reg_1['token'], 'dm_id': 1}
    response = requests.post(f"{BASE_URL}/dm/leave/v1", json = json_data)
    assert response.status_code == 400

def test_user_not_member(clear, user_reg_1, user_reg_2, user_reg_3):
    token = user_reg_1['token']
    u_id_2 = user_reg_2['auth_user_id']
    u_ids_list_2 = [u_id_2]
    dms_create_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token, 
        'u_ids': u_ids_list_2,
        })
    assert dms_create_response.status_code == 200
    dms_create_data = dms_create_response.json()
    dm_id = dms_create_data['dm_id']
    json_data = {'token': user_reg_3['token'], 'dm_id': dm_id}
    response = requests.post(f"{BASE_URL}/dm/leave/v1", json = json_data)
    assert response.status_code == 403

def test_successful_leave(clear, user_reg_1, user_reg_2):
    token = user_reg_1['token']
    u_id_2 = user_reg_2['auth_user_id']
    u_ids_list_2 = [u_id_2]
    dms_create_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token, 
        'u_ids': u_ids_list_2,
        })
    assert dms_create_response.status_code == 200
    dms_create_data = dms_create_response.json()
    dm_id = dms_create_data['dm_id']
    json_data = {'token': user_reg_2['token'], 'dm_id': dm_id}
    response = requests.post(f"{BASE_URL}/dm/leave/v1", json = json_data)
    assert response.status_code == 200

    dms_detail_response = requests.get(f"{BASE_URL}/dm/details/v1?token={token}&dm_id={dm_id}")
    assert dms_detail_response.status_code == 200
    dms_detail_response_data = dms_detail_response.json()

    user_resp_1 = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={user_reg_1['auth_user_id']}")
    assert user_resp_1.status_code == 200
    user_details_1 = user_resp_1.json()['user']
    assert len(dms_detail_response_data['members']) == 1
    assert dms_detail_response_data['members'][0]['u_id'] == user_details_1['u_id']
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
