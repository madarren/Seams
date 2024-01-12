"""
Tests for dm/message/v1
"""
import pytest
import requests
from src import config
from src.tokens import *

BASE_URL = config.url

valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
another_valid_user = {"email": "anothervalid@email.com", "password": "anotherpassword", "name_first": "firstname", "name_last": "lastname"}
valid_user_1 = {'email': 'valid22@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def user_1():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def user_2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)
    assert response.status_code == 200
    return response.json()

@pytest.fixture 
def dm_1(user_1, user_2):
    token = user_1['token']
    u_id = user_2['auth_user_id']
    u_ids_list = []
    u_ids_list.append(u_id)
    dms_create_response = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        'token': token, 
        'u_ids': u_ids_list,
        })
    assert dms_create_response.status_code == 200
    return dms_create_response.json()

def test_invalid_token(clear, dm_1):
    ''' Tests if the token is valid.'''
    token = 'jbvjkv'
    dm_id = dm_1['dm_id']
    start = 0
    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token}&dm_id={dm_id}&start={start}")
    assert response.status_code == 403

def test_token_not_in_dm(clear, dm_1):
    ''' Tests if the user is in dm.'''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_1)
    assert response.status_code == 200
    response_data = response.json()
    token = response_data['token']
    dm_id = dm_1['dm_id']
    start = 0
    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token}&dm_id={dm_id}&start={start}")
    assert response.status_code == 403

def test_invalid_dm_id(clear, user_1):
    ''' Tests if the dm_id is valid.'''
    token = user_1['token']
    dm_id = -1
    start = 0
    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token}&dm_id={dm_id}&start={start}")
    assert response.status_code == 400

def test_start_is_greater_current_messages(clear, user_1, dm_1):
    ''' Tests if start is greater than messages in dm.'''
    token = user_1['token']
    dm_id = dm_1['dm_id']
    start = 1
    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token}&dm_id={dm_id}&start={start}")
    assert response.status_code == 400

def test_dms_messages_works_with_no_messages(clear, user_1, dm_1):
    ''' Tests if dm/message/v1 with no message.'''
    token = user_1['token']
    dm_id = dm_1['dm_id']
    start = 0
    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token}&dm_id={dm_id}&start={start}")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {"messages": [], "start": 0, "end": -1}

def test_dms_messages_works_with_one_messages(clear, user_1, dm_1):
    ''' Tests if dm/message/v1 with one message.'''
    token = user_1['token']
    dm_id = dm_1['dm_id']
    start = 0

    send_message_response = requests.post(f"{BASE_URL}/message/senddm/v1", json = {
        'token': token, 
        'dm_id': dm_id,
        'message': 'Hello',
        })

    assert send_message_response.status_code == 200

    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token}&dm_id={dm_id}&start={start}")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["messages"][0]["message_id"] == 0    
    assert response_data["messages"][0]["message"] == "Hello" 


def test_over_fifty_messages(clear, user_1, dm_1):
    ''' test when over 50 messages are sent to a channel'''
    token = user_1['token']
    dm_id = dm_1['dm_id']
    for i in range(51):
        requests.post(f"{BASE_URL}/message/senddm/v1", json = {"token": token, "dm_id": dm_id, "message": str(-i)})
    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={token}&dm_id={dm_id}&start=0")
    
    assert response.status_code == 200
    
    message_list = response.json()["messages"]
    assert len(message_list) == 50
    for i in range(50):
        assert message_list[i]["message_id"] == 50 - i
        assert message_list[i]["message"] == str(i - 50)

    requests.delete(f"{BASE_URL}/clear/v1", json = {})
