'''
HTTP tests for channels_list_v2.

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
def user_reg_S():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert response.status_code == 200
    data = response.json()
    return data['token']


def test_channels_list_v2_invalid_user(clear):
    ''' Test that the invalid token raises AccessError '''
    response = requests.get(f"{BASE_URL}/channels/list/v2?token=abcdef")
    assert response.status_code == 403

def test_channels_list_v2_public_channel(clear, user_reg_S):
    ''' Test that the list is showing the user id and channel name correctly '''
    response = requests.post(f"{BASE_URL}/channels/create/v2", json= {
        'token': user_reg_S,
        'name': "channel_1",
        'is_public': True
        })
    assert response.status_code == 200
    list_response = requests.get(f"{BASE_URL}/channels/list/v2?token={user_reg_S}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data == {'channels': [{'channel_id': 0, 'name': 'channel_1'}]}

def test_channels_list_v2_not_joined(clear, user_reg_S):
    ''' Check if the user has not joined any channels '''
    list_response = requests.get(f"{BASE_URL}/channels/list/v2?token={user_reg_S}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data == {'channels': []}

def test_channels_list_v2_multiple_channels(clear, user_reg_S):
    ''' Test that the user is in multiple channels '''
    response = requests.post(f"{BASE_URL}/channels/create/v2", json= {
        'token': user_reg_S,
        'name': "channel_1",
        'is_public': True        
        })
    channel_1_id = response.json()['channel_id']
    response = requests.post(f"{BASE_URL}/channels/create/v2", json= {
        'token': user_reg_S,
        'name': "channel_2",
        'is_public': False
        })
    channel_2_id = response.json()['channel_id']
    list_response = requests.get(f"{BASE_URL}/channels/list/v2?token={user_reg_S}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    channel_1 = {'channel_id': channel_1_id, 'name': 'channel_1'}
    channel_2 = {'channel_id': channel_2_id, 'name': 'channel_2'}
    dict = []
    dict.append(channel_1)
    dict.append(channel_2)
    assert list_data == {'channels': dict}

def test_list_v2_two_channels(clear, user_reg_S):
    ''' Test when there are only two users and returns one users channel info '''
    valid_2_user = {'email': 'valid2@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    user2 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_2_user)
    user2_data = user2.json()['token']
    response = requests.post(f"{BASE_URL}/channels/create/v2", json= {
        'token': user_reg_S,
        'name': "channel_1",
        'is_public': True        
        })
    channel_1_id = response.json()['channel_id']
    response = requests.post(f"{BASE_URL}/channels/create/v2", json= {
        'token': user2_data,
        'name': "channel_2",
        'is_public': True
        })    
    list_response = requests.get(f"{BASE_URL}/channels/list/v2?token={user_reg_S}")
    assert list_response.status_code == 200
    list_data = list_response.json()
    channel_1 = {'channel_id': channel_1_id, 'name': 'channel_1'}
    dict = []
    dict.append(channel_1)
    assert list_data == {'channels': dict}

requests.delete(f"{BASE_URL}/clear/v1", json = {})
