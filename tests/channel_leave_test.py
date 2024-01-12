'''
Test file for channel_leave_v1, channel/leave/v1 (http)
'''

import pytest
from src.data_store import initial_object
from src.error import InputError, AccessError
from src.channel import *
from src.channels import *
from src.other import clear_v1
from src.auth import *
from src.tokens import *
import requests
from src import config

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'joel', 'name_last': 'embiid'}


@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_reg_S():
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    data = auth_login_v1('valid@email.com', 'password')
    return data

@pytest.fixture
def user_reg_S2():
    auth_register_v1('xyz@world.io', 'helloWorld', 'Python', 'Snake')
    data = auth_login_v1('xyz@world.io', 'helloWorld')
    return data

@pytest.fixture
def H_clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def H_user_reg_S():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def H_user_reg_S2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    assert response.status_code == 200
    return response.json()


def test_channel_leave_public(clear, user_reg_S, user_reg_S2):
    '''
    Test for success case of channel leave (Public)
    '''
    c_owner = user_reg_S['token']
    c_dict = channels_create_v1(c_owner, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    u_token = user_reg_S2['token']
    channel_join_v1(u_token, c_id)
    channel = initial_object['channels'][0]
    assert channel['members'][0] == user_reg_S['auth_user_id']
    assert channel['owners'][0] == user_reg_S['auth_user_id']
    assert channel['members'][1] == user_reg_S2['auth_user_id']

    channel_leave_v1(c_owner, c_id)
    assert channel['members'] == [user_reg_S2['auth_user_id']]
    assert channel['owners'] == []

def test_channel_leave_private(clear, user_reg_S, user_reg_S2):
    '''
    Test for success case of channel leave (Private)
    '''
    u_token = user_reg_S2['token']
    c_dict = channels_create_v1(u_token, 'SeamEgg', False)
    c_id = c_dict["channel_id"]
    S_owner = user_reg_S['token']
    channel_join_v1(S_owner, c_id)
    channel = initial_object['channels'][0]
    assert channel['members'][0] == user_reg_S2['auth_user_id']
    assert channel['owners'][0] == user_reg_S2['auth_user_id']
    assert channel['members'][1] == user_reg_S['auth_user_id']

    channel_leave_v1(S_owner, c_id)
    assert channel['members'] == [user_reg_S2['auth_user_id']]
    assert channel['owners'] == [user_reg_S2['auth_user_id']]

def test_channel_leave_invalid_token(clear, user_reg_S, user_reg_S2):
    '''
    Test if Accesserror is raised when token is invalid
    '''
    c_owner = user_reg_S['token']
    c_dict = channels_create_v1(c_owner, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    u_token = user_reg_S2['token']
    channel_join_v1(u_token, c_id)

    with pytest.raises(AccessError):
        channel_leave_v1("Undefined", c_id)

def test_channel_leave_invalid_channel_id(clear, user_reg_S, user_reg_S2):
    '''
    Test if Inputerror is raised when channel ID is invalid
    '''
    c_owner = user_reg_S['token']
    c_dict = channels_create_v1(c_owner, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    u_token = user_reg_S2['token']
    channel_join_v1(u_token, c_id)

    with pytest.raises(InputError):
        channel_leave_v1(u_token, 88888888)

def test_channel_leave_not_a_member(clear, user_reg_S, user_reg_S2):
    '''
    Test if Accesserror is raised when user leave a channel but not a member of the channel
    '''
    u_token = user_reg_S2['token']
    c_dict = channels_create_v1(u_token, 'SeamApple', True)
    c_id = c_dict["channel_id"]
    u_token2 = user_reg_S['token']

    with pytest.raises(AccessError):
        channel_leave_v1(u_token2, c_id)

def test_H_channel_leave_public(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test for success case of channel leave (Public)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/leave/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    token = H_user_reg_S['token']
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={H_user_reg_S['auth_user_id']}")
    user_details = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['name'] == 'Seam_Apple'
    assert c_data['is_public'] == True
    assert c_data['owner_members'][0]['u_id'] == user_details['user']['u_id']
    assert len(c_data['all_members']) == 1

def test_H_channel_leave_private(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test for success case of channel leave (Private)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Egg", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/leave/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    token = H_user_reg_S['token']
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['name'] == 'Seam_Egg'
    assert c_data['is_public'] == False
    assert c_data['owner_members'] == []
    assert len(c_data['all_members']) == 1

def test_H_channel_leave_invalid_token(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test if Accesserror is raised when token is invalid
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/leave/v1", json={"token": "Undefined", "channel_id": c_id})
    assert response.status_code == 403

def test_H_channel_leave_invalid_channel_id(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test if Inputerror is raised when channel ID is invalid
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/leave/v1", json={"token": H_user_reg_S['token'], "channel_id": 88888888})
    assert response.status_code == 400

def test_H_channel_leave_not_a_member(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test if Accesserror is raised when user leave a channel but not a member of the channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Egg", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/leave/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 403

def test_H_channel_leave_bad_request(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test for no input
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/leave/v1", json={})
    assert response.status_code == 500
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
