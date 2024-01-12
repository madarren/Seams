'''
Tests for channel/details/v2. i.e. http wrap of channel_details from iteration 1.
'''

from pickle import TRUE
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


def test_no_valid_token_or_channel(clear):
    ''' Test that an invalid token and channel id raises an AccessError. '''
    response = requests.get(f"{BASE_URL}/channel/details/v2?token=token&channel_id=999")
    assert response.status_code == 403 

def test_valid_token_invalid_channel(clear, new_user):
    ''' Test that a valid token but invalid channel id raises an InputError. '''
    token = new_user['token']
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id=999")
    assert response.status_code == 400

def test_token_not_in_channel(clear, new_user):
    ''' Test that a valid token not in the valid channel raises an AccessError. '''
    json_data = {"token": new_user['token'], "name": "Apple", "is_public": True}
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = json_data)
    chan_id = response.json()['channel_id']
    valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'name', 'name_last': 'name'}
    second_resp = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    sec_token = second_resp.json()['token']
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={sec_token}&channel_id={chan_id}")
    assert response.status_code == 403 

def test_get_details_one_user(clear, new_user):
    ''' Test that the correct details are returned for a channel with one user. '''
    json_data = {"token": new_user['token'], "name": "Apple", "is_public": True}
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = json_data)
    chan_id = response.json()['channel_id']
    token = new_user['token']
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={new_user['auth_user_id']}")
    user_details = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={chan_id}")
    assert response.status_code == 200
    chan_data = response.json()
    assert chan_data['name'] == 'Apple'
    assert chan_data['is_public'] == True
    assert chan_data['owner_members'][0]['u_id'] == user_details['user']['u_id']
    assert chan_data['all_members'][0]['u_id'] == user_details['user']['u_id']

requests.delete(f"{BASE_URL}/clear/v1", json = {})
