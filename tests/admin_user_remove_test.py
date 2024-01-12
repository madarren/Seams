'''
This file contains tests for the implementation of admin_user_remove_v1 and its http wrap
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
    valid_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'first', 'name_last': 'last'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()


def test_invalid_token_frontend(clear):
    ''' Test the function raises AccessError for invalid token. '''
    json_data = {'token': 'token', 'u_id': 1}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 403

def test_auth_user_not_global_owner(clear, new_user, new_user2):
    ''' Test function raises AccessError when auth user is to a global owner. '''
    json_data = {'token': new_user2['token'], 'u_id': 1}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 403

def test_invalid_u_id_frontend(clear, new_user):
    ''' Test function raises InputError when u_id is invalid. '''
    json_data = {'token': new_user['token'], 'u_id': 99}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 400

def test_one_global_owner(clear, new_user):
    ''' Test function raises InputError when u_id is the only global owner. '''
    json_data = {'token': new_user['token'], 'u_id': new_user['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 400

def test_once_removed_user_cant_do_anything(clear, new_user, new_user2):
    ''' Test successful removal stops the user from doing anything, i.e. AccessError on their tokens. '''
    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 200
    logout_data = {'token': new_user2['token']}
    logout_resp = requests.post(f"{BASE_URL}/auth/logout/v1", json = logout_data)
    assert logout_resp.status_code == 403

def test_removal_removed_from_channel(clear, new_user, new_user2):
    ''' Test successful removal from channels. '''
    chan_create_data = {'token': new_user['token'], 'name': 'Apple', 'is_public': True}
    create_resp = requests.post(f"{BASE_URL}/channels/create/v2", json = chan_create_data)
    assert create_resp.status_code == 200
    c_id = create_resp.json()['channel_id']
    chan_join_data = {'token': new_user2['token'], 'channel_id': c_id}
    join_resp = requests.post(f"{BASE_URL}/channel/join/v2", json = chan_join_data)
    assert join_resp.status_code == 200

    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 200
    details_resp = requests.get(f"{BASE_URL}/channel/details/v2?token={new_user['token']}&channel_id={c_id}")
    assert details_resp.status_code == 200
    members = details_resp.json()['all_members']
    assert new_user2['auth_user_id'] not in [m['u_id'] for m in members]

def test_remove_channel_owner(clear, new_user, new_user2):
    ''' Test successful removal of a channel owner. '''
    chan_create_data = {'token': new_user2['token'], 'name': 'Apple', 'is_public': True}
    create_resp = requests.post(f"{BASE_URL}/channels/create/v2", json = chan_create_data)
    assert create_resp.status_code == 200
    c_id = create_resp.json()['channel_id']
    chan_create_data = {'token': new_user2['token'], 'name': 'apple', 'is_public': False}
    requests.post(f"{BASE_URL}/channels/create/v2", json = chan_create_data)
    chan_create_data = {'token': new_user['token'], 'name': 'bpple', 'is_public': False}
    requests.post(f"{BASE_URL}/channels/create/v2", json = chan_create_data)
    chan_join_data = {'token': new_user['token'], 'channel_id': c_id}
    join_resp = requests.post(f"{BASE_URL}/channel/join/v2", json = chan_join_data)
    assert join_resp.status_code == 200

    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 200
    details_resp = requests.get(f"{BASE_URL}/channel/details/v2?token={new_user['token']}&channel_id={c_id}")
    assert details_resp.status_code == 200
    members = details_resp.json()['all_members']
    assert new_user2['auth_user_id'] not in [m['u_id'] for m in members]

def test_removal_removed_from_dm(clear, new_user, new_user2):
    ''' Test successful removal from dms. '''
    dm_create_data = {'token': new_user['token'], 'u_ids': [new_user2['auth_user_id']]}
    create_resp = requests.post(f"{BASE_URL}/dm/create/v1", json = dm_create_data)
    assert create_resp.status_code == 200
    dm_id = create_resp.json()['dm_id']

    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 200
    details_resp = requests.get(f"{BASE_URL}/dm/details/v1?token={new_user['token']}&dm_id={dm_id}")
    assert details_resp.status_code == 200
    members = details_resp.json()['members']
    assert new_user2['auth_user_id'] not in [m['u_id'] for m in members]

def test_removal_not_in_users_all(clear, new_user, new_user2):
    ''' Test removed user does not appear in the users all function return. '''
    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 200
    user_resp = requests.get(f"{BASE_URL}/users/all/v1?token={new_user['token']}")
    assert user_resp.status_code == 200
    users = user_resp.json()['users']
    assert new_user2['auth_user_id'] not in [u['u_id'] for u in users]

def test_email_reusable(clear, new_user, new_user2):
    ''' Test removed user's email can be reused. '''
    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 200
    valid_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'first', 'name_last': 'last'}
    rereg_resp = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert rereg_resp.status_code == 200

def test_handle_reusable(clear, new_user, new_user2):
    ''' Test removed user's handle can be reused. '''
    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 200
    json_handle = {'token': new_user['token'], 'handle_str': 'firstlast'}
    handle_resp = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json = json_handle)
    assert handle_resp.status_code == 200

def test_messages_after_user_removal_correct_format_ch(clear, new_user, new_user2):
    ''' Test message content of removed user is now 'Removed user'. '''
    chan_create_data = {'token': new_user['token'], 'name': 'Apple', 'is_public': True}
    create_resp = requests.post(f"{BASE_URL}/channels/create/v2", json = chan_create_data)
    c_id = create_resp.json()['channel_id']
    chan_join_data = {'token': new_user2['token'], 'channel_id': c_id}
    requests.post(f"{BASE_URL}/channel/join/v2", json = chan_join_data)

    json_body = {"token": new_user2["token"], "channel_id": c_id, "message": "Hello World"}
    requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]

    json_body = {"token": new_user2["token"], "channel_id": c_id, "message": "HELLO WORLD"}
    requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]

    token_1 = new_user["token"]

    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={token_1}&channel_id={c_id}&start=0")
    assert response.json()["messages"][1]["message"] == "Hello World"
    assert response.json()["messages"][0]["message"] == "HELLO WORLD"

    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)

    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={token_1}&channel_id={c_id}&start=0")
    assert response.json()["messages"][0]["message"] == "Removed user"
    assert response.json()["messages"][1]["message"] == "Removed user"

def test_messages_after_user_removal_correct_format_dm(clear, new_user, new_user2):
    ''' Test message content of removed user is now 'Removed user'. '''
    chan_create_data = {'token': new_user['token'], 'u_ids': [new_user2["auth_user_id"]]}
    create_resp = requests.post(f"{BASE_URL}/dm/create/v1", json = chan_create_data)
    dm_id = create_resp.json()['dm_id']

    json_body = {"token": new_user2["token"], "dm_id": dm_id, "message": "Hello World"}
    requests.post(f"{BASE_URL}/message/senddm/v1", json = json_body).json()["message_id"]

    json_body = {"token": new_user2["token"], "dm_id": dm_id, "message": "HELLO WORLD"}
    requests.post(f"{BASE_URL}/message/senddm/v1", json = json_body).json()["message_id"]

    token_1 = new_user["token"]

    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token_1}&dm_id={dm_id}&start=0")
    assert response.json()["messages"][1]["message"] == "Hello World"
    assert response.json()["messages"][0]["message"] == "HELLO WORLD"

    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)

    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token_1}&dm_id={dm_id}&start=0")
    assert response.json()["messages"][0]["message"] == "Removed user"
    assert response.json()["messages"][1]["message"] == "Removed user"
    

def test_removed_profile_still_fetchable_with_user_profile(clear, new_user, new_user2):
    ''' Test user profile is fetchable but is now 'Removed user'. '''
    json_data = {'token': new_user['token'], 'u_id': new_user2['auth_user_id']}
    response = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json = json_data)
    assert response.status_code == 200
    profile_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={new_user['token']}&u_id={new_user2['auth_user_id']}")
    assert profile_resp.status_code == 200
    profile = profile_resp.json()['user']
    assert profile['name_first'] == 'Removed' and profile['name_last'] == 'user'
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
