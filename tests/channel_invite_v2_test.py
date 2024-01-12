'''
Tests for channel/invite/v2. i.e. http wrap of channel_invite_v from iteration 1.
'''

import pytest
import requests
from src import config

BASE_URL = config.url

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def user_registration():
    valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()

@pytest.fixture
def user_reg2():
    valid_user = {'email': 'valid1@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()

@pytest.fixture
def channel_reg(user_registration):
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = {
        "token": user_registration['token'], 
        "name": "channel_test", 
        "is_public": True
    })
    channel_response_data = response.json()
    return channel_response_data['channel_id']

 
def test_invalid_user(clear, user_registration, channel_reg):
    ''' Test that access error is returned for invalid token. '''
    response = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': 'jdfjks',
        'channel_id': channel_reg,
        'u_id': user_registration['auth_user_id']
    })
    assert response.status_code == 403

def test_invalid_channel_id(clear, user_registration):
    ''' Test that it raises input error when channel_id is invalid. '''
    response = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': user_registration['token'],
        'channel_id': -1,
        'u_id': 99
    })
    assert response.status_code == 400

def test_auth_user_not_member(clear, user_registration, channel_reg):
    ''' Test that it raises access error when the auth user was not a member of the channel. '''
    params = {'email': 'valid2@email.com', 'password': 'password', 'name_first': 'valid2', 'name_last': 'lastname'}
    another_user_response = requests.post(f"{BASE_URL}/auth/register/v2", json = params)
    another_user_response_data = another_user_response.json()
    another_user_token = another_user_response_data['token']
    response = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': another_user_token,
        'channel_id': channel_reg,
        'u_id': user_registration['auth_user_id'],
    })
    assert response.status_code == 403

def test_invalid_u_id(clear, user_registration, channel_reg):
    ''' Test that it raises input error when u_id is invalid. '''
    response = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': user_registration['token'],
        'channel_id': channel_reg,
        'u_id': -1
    })
    assert response.status_code == 400

def test_u_id_already_member(clear, user_registration, channel_reg):
    ''' Test inviting an existing user raises an InputError. '''
    response = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        'token': user_registration['token'],
        'channel_id': channel_reg,
        'u_id': user_registration['auth_user_id'],
    })
    assert response.status_code == 400

def test_valid_invite(clear, user_registration, user_reg2, channel_reg):
    ''' Test that channel_invite_v1 functions properly. '''
    param = {'token': user_registration['token'], 'channel_id': channel_reg, 'u_id': user_reg2['auth_user_id']}
    response = requests.post(f"{BASE_URL}/channel/invite/v2", json= param)
    assert response.status_code == 200
    token = user_reg2['token']
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={channel_reg}")
    assert response.status_code == 200
    data = response.json()['all_members']
    user2_id = user_reg2['auth_user_id']
    assert user2_id == data[1]['u_id']
    response = requests.post(f"{BASE_URL}/channel/invite/v2", json= param)
    assert response.status_code == 400

requests.delete(f"{BASE_URL}/clear/v1", json = {})
