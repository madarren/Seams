"""
Tests for message/sendlaterdm/v1
"""


import pytest
import requests
import datetime, time
from src import config
import string 
import random

BASE_URL = config.url

valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
another_valid_user = {"email": "anothervalid@email.com", "password": "anotherpassword", "name_first": "firstname", "name_last": "lastname"}
valid_user_1 = {'email': 'valid1@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
    

@pytest.fixture
def user_1():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()

@pytest.fixture
def user_2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)
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

def test_token_invalid(clear, dm_1):
    ''' Test valid token '''
    token = -1
    dm_id = dm_1['dm_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 3600

    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert response.status_code == 403

def test_auth_user_not_member(clear, dm_1):
    ''' Test valid authorised user is a member of the dm '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_1)
    assert response.status_code == 200
    response_data = response.json()
    token = response_data['token']
    dm_id = dm_1['dm_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 3600

    dm_response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert dm_response.status_code == 403


def test_dm_id_invalid(clear, user_1):
    ''' Test dm_id is valid '''
    token = user_1['token']
    dm_id = -1
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 3600

    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert response.status_code == 400

def test_time_is_in_the_past(clear, user_1, dm_1):
    ''' Test when time_sent is in the past '''
    token = user_1['token']
    dm_id = dm_1['dm_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) - 3600
    

    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert response.status_code == 400

def test_message_too_long(clear, user_1, dm_1):
    ''' Message exceeds 1000 characters'''
    long_message = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    token = user_1['token']
    dm_id = dm_1['dm_id']
    time_sent = int(datetime.datetime.now().timestamp()) + 3600
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': long_message,
        'time_sent': time_sent,
    })
    assert response.status_code == 400

def test_message_too_short(clear, user_1, dm_1):
    ''' Message is less than 1 character '''
    token = user_1['token']
    dm_id = dm_1['dm_id']
    time_sent = int(datetime.datetime.now().timestamp()) + 3600
    message = ""
    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent,
    })
    assert response.status_code == 400

def test_message_sendlaterdm_works(clear, user_1, dm_1):
    ''' Test functionality of the function by checking the message_id returned is correct '''
    token = user_1['token']
    dm_id = dm_1['dm_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 2
    

    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent,

    })
    assert response.status_code == 200
    time.sleep(2)
    
    response_data = response.json()
    assert response_data['message_id'] == 0

def test_dm_deleted(clear, user_1, dm_1):
    ''' Test functionality of the function by checking the message_id returned is correct '''
    token = user_1['token']
    dm_id = dm_1['dm_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 2
    
    json_body = {"token": token, "dm_id": dm_id, "message": "Hello World"}
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json = json_body)

    response = requests.get(f"{BASE_URL}/users/stats/v1?token={token}")
    assert response.json()['workspace_stats']['messages_exist'][-1]["num_messages_exist"] == 1

    response = requests.post(f"{BASE_URL}/message/sendlaterdm/v1", json = {
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent,

    })
    requests.delete(f"{BASE_URL}/dm/remove/v1", json = {"token": token, "dm_id": dm_id})
    assert response.status_code == 200
    time.sleep(2)
    
    response_data = response.json()
    assert response_data['message_id'] == 1

    response = requests.get(f"{BASE_URL}/users/stats/v1?token={token}")
    assert response.json()['workspace_stats']['messages_exist'][-1]["num_messages_exist"] == 0

    requests.delete(f"{BASE_URL}/clear/v1", json = {})
