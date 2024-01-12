'''
Test file for channel/join/v2 (http).
'''
import pytest
from src.data_store import initial_object
from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v1
from src.tokens import *
import requests
from src import config

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'joel', 'name_last': 'embiid'}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def user_reg_S():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def user_reg_S2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    assert response.status_code == 200
    return response.json()

def test_channel_join_public_succuss(clear, user_reg_S, user_reg_S2):
    '''
    Test for success case for user joining existing channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    assert c_id == 0
    token = user_reg_S['token']
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={user_reg_S['auth_user_id']}")
    user_details = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['name'] == 'Seam_Apple'
    assert c_data['is_public'] == True
    assert c_data['owner_members'][0]['u_id'] == user_details['user']['u_id']
    assert c_data['all_members'][0]['u_id'] == user_details['user']['u_id']


    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200
    token = user_reg_S2['token']
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={user_reg_S2['auth_user_id']}")
    user_details2 = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['name'] == 'Seam_Apple'
    assert c_data['is_public'] == True
    assert c_data['owner_members'][0]['u_id'] == user_details['user']['u_id']
    assert c_data['all_members'][1]['u_id'] == user_details2['user']['u_id']

def test_channel_join_private_fail(clear, user_reg_S, user_reg_S2):
    '''
    Test if Accesserror is raised when a normal user tried to join a private channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S['token'], "name": "Seam_Egg", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 403

def test_channel_join_bad_request(clear, user_reg_S, user_reg_S2):
    '''
    Test for no input
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={})
    assert response.status_code == 500

def test_channel_join_invalid_token(clear, user_reg_S, user_reg_S2):
    '''
    Test if Accesserror is raised when token is invalid
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": "Undefined", "channel_id": c_id})
    assert response.status_code == 403

def test_channel_join_channel_id_not_found(clear, user_reg_S):
    '''
    Test if Inputerror is raised when channel ID no exist / invalid
    '''
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": user_reg_S['token'], "channel_id": 88888888})
    assert response.status_code == 400

def test_channel_join_is_member_already(clear, user_reg_S, user_reg_S2):
    '''
    Test if Inputerror is raised when user tried to join but already a member of the channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 400

def test_channel_join_public_Seamfounder(clear, user_reg_S, user_reg_S2):
    '''
    Test if global owner able to join the channel (Public)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S2['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": user_reg_S['token'], "channel_id": c_id})
    assert response.status_code == 200
    token = user_reg_S['token']
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={user_reg_S['auth_user_id']}")
    user_details = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['all_members'][1]['u_id'] == user_details['user']['u_id']

def test_channel_join_private_Seamfounder(clear, user_reg_S, user_reg_S2):
    '''
    Test if global owner able to join the channel (Private)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S2['token'], "name": "Seam_Egg", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": user_reg_S['token'], "channel_id": c_id})
    assert response.status_code == 200
    token = user_reg_S['token']
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={user_reg_S['auth_user_id']}")
    user_details = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['all_members'][1]['u_id'] == user_details['user']['u_id']
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
