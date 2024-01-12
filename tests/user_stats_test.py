'''
This file contains tests for the implementation of user stats and its http wrap.
'''
import pytest
import requests
from src import config

BASE_URL = config.url

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def new_user():
    valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()

@pytest.fixture
def new_user2():
    valid_user2 = {'email': 'valid2@email.com', 'password': 'password', 'name_first': 'first', 'name_last': 'last'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user2)
    return response.json()

def test_invalid_token(clear):
    ''' Test the function raises AccessError for invalid token. '''
    response = requests.get(f"{BASE_URL}/user/stats/v1?token=token")
    assert response.status_code == 403

def test_no_involvement(clear, new_user):
    ''' Test when user has no involvement. '''
    response = requests.get(f"{BASE_URL}/user/stats/v1?token={new_user['token']}")
    assert response.status_code == 200
    assert len(response.json()['user_stats']['channels_joined']) == 1
    assert response.json()['user_stats']['involvement_rate'] == 0

def test_create_channel(clear, new_user):
    ''' Test correct function return for user after creating a channel. '''
    chan_create_data = {'token': new_user['token'], 'name': 'Apple', 'is_public': True}
    requests.post(f"{BASE_URL}/channels/create/v2", json = chan_create_data)
    response = requests.get(f"{BASE_URL}/user/stats/v1?token={new_user['token']}")
    assert response.status_code == 200
    assert response.json()['user_stats']['channels_joined'][1]['num_channels_joined'] == 1
    assert response.json()['user_stats']['involvement_rate'] == 1

def test_one_channel_join_and_leave(clear, new_user, new_user2):
    ''' Test function returns correct list of dictionaries for user who enters and leaves a channel. '''
    chan_create_data = {'token': new_user['token'], 'name': 'Apple', 'is_public': True}
    chan_create_resp = requests.post(f"{BASE_URL}/channels/create/v2", json = chan_create_data)
    c_id = chan_create_resp.json()['channel_id']
    chan_join_data = {"token": new_user2['token'], "channel_id": c_id}
    requests.post(f"{BASE_URL}/channel/join/v2", json=chan_join_data)
    chan_leave_data = {"token": new_user2['token'], "channel_id": c_id}
    requests.post(f"{BASE_URL}/channel/leave/v1", json=chan_leave_data)
    response = requests.get(f"{BASE_URL}/user/stats/v1?token={new_user2['token']}")
    assert response.status_code == 200
    assert len(response.json()['user_stats']['channels_joined']) == 3
    assert response.json()['user_stats']['channels_joined'][-1]['num_channels_joined'] == 0
    assert response.json()['user_stats']['involvement_rate'] == 0

def test_channel_invite(clear, new_user, new_user2):
    ''' Test correct function return for user invited to a channel. '''
    chan_create_data = {'token': new_user['token'], 'name': 'Apple', 'is_public': True}
    chan_create_resp = requests.post(f"{BASE_URL}/channels/create/v2", json = chan_create_data)
    c_id = chan_create_resp.json()['channel_id']
    chan_invite_data = {'token': new_user['token'], 'channel_id': c_id, 'u_id': new_user2['auth_user_id']}
    requests.post(f"{BASE_URL}/channel/invite/v2", json=chan_invite_data)
    response = requests.get(f"{BASE_URL}/user/stats/v1?token={new_user2['token']}")
    assert response.status_code == 200
    assert len(response.json()['user_stats']['channels_joined']) == 2
    assert response.json()['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1
    assert response.json()['user_stats']['involvement_rate'] == 1

def test_one_dm_create_and_leave(clear, new_user, new_user2):
    ''' Test correct function return for when a user makes a dm and leaves. '''
    dm_create_data = {'token': new_user['token'], 'u_ids': [new_user2['auth_user_id']]}
    create_resp = requests.post(f"{BASE_URL}/dm/create/v1", json = dm_create_data)
    dm_id = create_resp.json()['dm_id']
    dm_leave_data = {'token': new_user2['token'], 'dm_id': dm_id}
    requests.post(f"{BASE_URL}/dm/leave/v1", json = dm_leave_data)
    user2_response = requests.get(f"{BASE_URL}/user/stats/v1?token={new_user2['token']}")
    assert user2_response.status_code == 200
    assert len(user2_response.json()['user_stats']['dms_joined']) == 3
    assert user2_response.json()['user_stats']['dms_joined'][-1]['num_dms_joined'] == 0
    assert user2_response.json()['user_stats']['involvement_rate'] == 0

    user1_response = requests.get(f"{BASE_URL}/user/stats/v1?token={new_user['token']}")
    assert user1_response.status_code == 200
    assert len(user1_response.json()['user_stats']['dms_joined']) == 2
    assert user1_response.json()['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1
    assert user1_response.json()['user_stats']['involvement_rate'] == 1

def test_dm_remove(clear, new_user, new_user2):
    ''' Test correct return for when a user makes a dm but removes it. '''
    dm_create_data = {'token': new_user['token'], 'u_ids': [new_user2['auth_user_id']]}
    create_resp = requests.post(f"{BASE_URL}/dm/create/v1", json = dm_create_data)
    dm_id = create_resp.json()['dm_id']
    dm_remove_data = {'token': new_user['token'], 'dm_id': dm_id}
    requests.delete(f"{BASE_URL}/dm/remove/v1", json = dm_remove_data)

    response = requests.get(f"{BASE_URL}/user/stats/v1?token={new_user['token']}")
    assert response.status_code == 200
    assert len(response.json()['user_stats']['dms_joined']) == 3
    assert response.json()['user_stats']['involvement_rate'] == 0
