'''
This file contains tests for the implementation of the incomplete functions and their http wrap.
'''
import pytest
import requests
from src import config
import random
import string

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


def test_invalid_token_notifications(clear):
    ''' Test notifications raises AccessError for invalid token. '''
    response = requests.get(f"{BASE_URL}/notifications/get/v1?token=token")
    assert response.status_code == 403

def test_return_notifications(clear, new_user):
    ''' Test the return of notifications. '''
    response = requests.get(f"{BASE_URL}/notifications/get/v1?token={new_user['token']}")
    assert response.status_code == 200
    assert response.json()['notifications'] == []

def test_invalid_token_search(clear):
    ''' Test search raises AccessError for invalid token. '''
    response = requests.get(f"{BASE_URL}/search/v1?token=token&query_str={''}")
    assert response.status_code == 403

def test_invalid_query(clear, new_user):
    ''' Test search raises InputError for and invalid query_str '''
    response = requests.get(f"{BASE_URL}/search/v1?token={new_user['token']}&query_str={''}")
    assert response.status_code == 400

def test_return_search(clear, new_user):
    ''' Test the return of search. '''
    response = requests.get(f"{BASE_URL}/search/v1?token={new_user['token']}&query_str={'aye'}")
    assert response.status_code == 200
    assert response.json()['messages'] == []


def test_message_share_invalid_token(clear):
    ''' Test message share raises AccessError for invalid token. '''
    json_data = {"token": "invalidtoken", "og_message_id": 0, "message": "a", "channel_id": 0, "dm_id": 0}
    response = requests.post(f"{BASE_URL}/message/share/v1", json = json_data)
    assert response.status_code == 403

def test_message_share_channel_and_dm_id(clear, new_user):
    ''' Test message share raises InputError for invalid channel and dm id. '''
    json_data = {"token": new_user['token'], "og_message_id": 0, "message": "a", "channel_id": 1, "dm_id": 1}
    response = requests.post(f"{BASE_URL}/message/share/v1", json = json_data)
    assert response.status_code == 400

def test_message_share_no_minus_1_id(clear, new_user):
    ''' Test message share raises InputError for missing -1 in channel and dm id. '''
    chan_data = {'token': new_user['token'], 'name': 'apple', 'is_public': True}
    chan_resp = requests.post(f"{BASE_URL}/channels/create/v2", json=chan_data)
    c_id = chan_resp.json()['channel_id']
    json_data = {"token": new_user['token'], "og_message_id": 0, "message": "a", "channel_id": c_id, "dm_id": 0}
    response = requests.post(f"{BASE_URL}/message/share/v1", json = json_data)
    assert response.status_code == 400

def test_message_share_user_in_share(clear, new_user, new_user2):
    ''' Test message share raises AccessError for when  they are not in channel/dm to be shared. '''
    dm_create_data = {'token': new_user['token'], 'u_ids': [new_user2['auth_user_id']]}
    create_resp = requests.post(f"{BASE_URL}/dm/create/v1", json = dm_create_data)
    dm_id = create_resp.json()['dm_id']
    chan_data = {'token': new_user['token'], 'name': 'apple', 'is_public': True}
    chan_resp = requests.post(f"{BASE_URL}/channels/create/v2", json=chan_data)
    c_id = chan_resp.json()['channel_id']

    json1_data = {"token": new_user2['token'], "og_message_id": 0, "message": "a", "channel_id": c_id, "dm_id": -1}
    response = requests.post(f"{BASE_URL}/message/share/v1", json = json1_data)
    assert response.status_code == 403

    dm_leave_data = {'token': new_user2['token'], 'dm_id': dm_id}
    requests.post(f"{BASE_URL}/dm/leave/v1", json = dm_leave_data)
    json2_data = {"token": new_user2['token'], "og_message_id": 0, "message": "a", "channel_id": -1, "dm_id": dm_id}
    response2 = requests.post(f"{BASE_URL}/message/share/v1", json = json2_data)
    assert response2.status_code == 403

def test_message_share_invalid_message(clear, new_user):
    ''' Test InputError raised when message is too long. '''
    large_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1001))
    chan_data = {'token': new_user['token'], 'name': 'apple', 'is_public': True}
    chan_resp = requests.post(f"{BASE_URL}/channels/create/v2", json=chan_data)
    c_id = chan_resp.json()['channel_id']
    json1_data = {"token": new_user['token'], "og_message_id": 0, "message": large_string, "channel_id": c_id, "dm_id": -1}
    response = requests.post(f"{BASE_URL}/message/share/v1", json = json1_data)
    assert response.status_code == 400

def test_return_message_share(clear, new_user):
    ''' Test return of message share. '''
    chan_data = {'token': new_user['token'], 'name': 'apple', 'is_public': True}
    chan_resp = requests.post(f"{BASE_URL}/channels/create/v2", json=chan_data)
    c_id = chan_resp.json()['channel_id']

    json_data = {"token": new_user['token'], "og_message_id": 0, "message": '','' "channel_id": c_id, "dm_id": -1}
    response = requests.post(f"{BASE_URL}/message/share/v1", json = json_data)
    assert response.status_code == 200
    assert response.json()['shared_message_id'] == 1

def test_og_message_id_fake(clear, new_user):
    ''' Test when og_message_id is not an int. '''
    chan_data = {'token': new_user['token'], 'name': 'apple', 'is_public': True}
    chan_resp = requests.post(f"{BASE_URL}/channels/create/v2", json=chan_data)
    c_id = chan_resp.json()['channel_id']

    json_data = {"token": new_user['token'], "og_message_id": 'a', "message": '','' "channel_id": c_id, "dm_id": -1}
    response = requests.post(f"{BASE_URL}/message/share/v1", json = json_data)
    assert response.status_code == 200
    assert response.json()['shared_message_id'] == 1

    requests.delete(f"{BASE_URL}/clear/v1", json = {})
