"""
Tests for message/sendlater/v1
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
def channel_1(user_1):
    token = user_1['token']
    json_body = {"token": token, "name": "channel 1", "is_public": True}
    return requests.post(f"{BASE_URL}/channels/create/v2", json = json_body).json()

def test_token_invalid(clear, channel_1):
    ''' Test valid token '''
    token = -1
    channel_id = channel_1['channel_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 3600

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert response.status_code == 403

def test_auth_user_not_member(clear, channel_1):
    ''' Test valid authorised user is a member of the channel '''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user_1)
    response_data = response.json()
    token = response_data['token']
    channel_id = channel_1['channel_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 3600

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert response.status_code == 403


def test_channel_id_invalid(clear, user_1):
    ''' Test channel_id is valid '''
    token = user_1['token']
    channel_id = -1
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 3600

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert response.status_code == 400

def test_time_is_in_the_past(clear, user_1, channel_1):
    ''' Test when time_sent is in the past '''
    token = user_1['token']
    channel_id = channel_1['channel_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) - 3600
    

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert response.status_code == 400

def test_message_too_long(clear, user_1, channel_1):
    ''' Message exceeds 1000 characters'''
    long_message = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    token = user_1['token']
    channel_id = channel_1['channel_id']
    time_sent = int(datetime.datetime.now().timestamp()) + 3600
    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': long_message,
        'time_sent': time_sent,
    })
    assert response.status_code == 400

def test_message_too_short(clear, user_1, channel_1):
    ''' message is less than 1 character'''
    token = user_1['token']
    channel_id = channel_1['channel_id']
    time_sent = int(datetime.datetime.now().timestamp()) + 3600
    message = ""
    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent,
    })
    assert response.status_code == 400

def test_message_sendlater_works(clear, user_1, channel_1):
    ''' Test functionality of the function by checking the message_id returned is correct '''
    token = user_1['token']
    channel_id = channel_1['channel_id']
    message = 'Hello'
    time_sent = int(datetime.datetime.now().timestamp()) + 2
    

    response = requests.post(f"{BASE_URL}/message/sendlater/v1", json = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent,

    })

    assert response.status_code == 200
    time.sleep(2)

    response_data = response.json()
    assert response_data['message_id'] == 0


requests.delete(f"{BASE_URL}/clear/v1", json = {})