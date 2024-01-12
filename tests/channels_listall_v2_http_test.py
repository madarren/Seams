'''
HTTP tests for channels_listall_v2.
'''
import pytest
from src import config
import requests

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def user_reg():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()['token']


def test_invalid_token(clear):
    ''' Test AccessError is raised when invalid token is given. '''
    response = requests.get(f"{BASE_URL}/channels/listall/v2?token=abcdef")
    assert response.status_code == 403

def test_no_channels(clear, user_reg):
    ''' Test function works even with no channels. '''
    response = requests.get(f"{BASE_URL}/channels/listall/v2?token={user_reg}")
    assert response.status_code == 200
    list_data = response.json()
    assert list_data == {'channels': []}

def test_one_channel(clear, user_reg):
    ''' Test the function works with one channel. '''
    json_data = {'token': user_reg, 'name': 'Channel 1', 'is_public': True}
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = json_data)
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    list_response = requests.get(f"{BASE_URL}/channels/listall/v2?token={user_reg}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data == {'channels': [{'channel_id': c_id, 'name': 'Channel 1'}]}

def test_listall_two_channels(clear, user_reg):
    ''' Test function works with private and public channels, with different members. '''
    new_user_json = {'email': 'second@email.com', 'password': 'password', 'name_first': 'first', 'name_last': 'last'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = new_user_json)
    token2 = response.json()['token']
    c1_data = {'token': user_reg, 'name': 'Channel 1', 'is_public': True}
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = c1_data)
    c1_id = response.json()['channel_id']
    c2_data = {'token': token2, 'name': 'Channel 2', 'is_public': False}
    response = requests.post(f"{BASE_URL}/channels/create/v2", json = c2_data)
    c2_id = response.json()['channel_id']
    channel_1 = {'channel_id': c1_id, 'name': 'Channel 1'}
    channel_2 = {'channel_id': c2_id, 'name': 'Channel 2'}
    dict = []
    dict.append(channel_1)
    dict.append(channel_2)
    list_response = requests.get(f"{BASE_URL}/channels/listall/v2?token={user_reg}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data == {'channels': dict}

requests.delete(f"{BASE_URL}/clear/v1", json = {})
