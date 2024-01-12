'''
This file contains tests for the implementation of message_send_v1 and its http wrap.

'''

import pytest
from src.message import message_send_v1
from src.error import AccessError, InputError 
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
import requests
from src import config

import string 
import random

BASE_URL = config.url
URL = BASE_URL + "/message/send/v1"

valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
another_valid_user = {"email": "anothervalid@email.com", "password": "anotherpassword", "name_first": "firstname", "name_last": "lastname"}


@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
    clear_v1()

@pytest.fixture
def user_reg_S():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()["token"]

@pytest.fixture
def another_user_reg_S():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)
    return response.json()["token"]

@pytest.fixture 
def channel_reg_S(user_reg_S):
    json_body = {"token": user_reg_S, "name": "channel 1", "is_public": True}
    return requests.post(f"{BASE_URL}/channels/create/v2", json = json_body).json()["channel_id"]

def test_invalid_user_B(clear):
    ''' invalid token (and channel but AccessError has higher priority)'''
    with pytest.raises(AccessError):
        message_send_v1("invalidtoken", 3, "Hello World")


def test_invalid_user_HTTP(clear):
    ''' invalid token (and channel but AccessError has higher priority)'''
    json_body = {"token": "invalidtoken", "channel_id": 3, "message": "Hello World"}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 403 

def test_invalid_channel_B(clear):
    ''' invalid channel_id (valid token now)'''
    user_reg_S = auth_register_v1("valid@email.com", "password", "namefirst", "namelast")['token']
    with pytest.raises(InputError):
        message_send_v1(user_reg_S, 3, "Hello World")


def test_invalid_channel_HTTP(clear, user_reg_S):
    ''' invalid channel_id (valid token now)'''
    json_body = {"token": user_reg_S, "channel_id": 3, "message": "Hello World"}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 400

def test_message_too_long_B(clear):
    user_reg_S = auth_register_v1("valid@email.com", "password", "namefirst", "namelast")['token']
    channel_reg_S = channels_create_v1(user_reg_S, "Channel 1", True)["channel_id"]
    long_message = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    with pytest.raises(InputError):
        message_send_v1(user_reg_S, channel_reg_S, long_message)

def test_message_too_long_HTTP(clear, user_reg_S, channel_reg_S):
    ''' message exceeds 1000 characters'''
    long_message = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    json_body = {"token": user_reg_S, "channel_id": channel_reg_S, "message": long_message}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 400

def test_message_too_short_B(clear):
    user_reg_S = auth_register_v1("valid@email.com", "password", "namefirst", "namelast")['token']
    channel_reg_S = channels_create_v1(user_reg_S, "Channel 1", True)["channel_id"]
    with pytest.raises(InputError):
        message_send_v1(user_reg_S, channel_reg_S, "")

def test_message_too_short_HTTP(clear, user_reg_S, channel_reg_S):
    ''' message is 0 chars (empty)'''
    json_body = {"token": user_reg_S, "channel_id": channel_reg_S, "message": ""}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 400

def test_auth_user_non_member_B(clear, user_reg_S, channel_reg_S, another_user_reg_S):
    ''' test token used to call route is not actually in the channel'''
    user_reg_S = auth_register_v1("valid@email.com", "password", "namefirst", "namelast")['token']
    channel_reg_S = channels_create_v1(user_reg_S, "Channel 1", True)["channel_id"]
    another_user_reg_S = auth_register_v1("anothervalid@email.com", "password", "firstname", "lastname")["token"]

    with pytest.raises(AccessError):
        message_send_v1(another_user_reg_S, channel_reg_S, "HelloWorld")

def test_auth_user_non_member_HTTP(clear, user_reg_S, channel_reg_S, another_user_reg_S):
    ''' test token used to call route is not actually in the channel'''
    json_body = {"token": another_user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 403

def test_message_sent_B(clear):
    user_reg_S = auth_register_v1("valid@email.com", "password", "namefirst", "namelast")['token']
    channel_reg_S = channels_create_v1(user_reg_S, "Channel 1", True)["channel_id"]
    message_id = message_send_v1(user_reg_S, channel_reg_S, "Hello World")["message_id"]
    assert message_id == 0


def test_message_sent_S_HTTP(clear, user_reg_S, channel_reg_S):
    ''' test a message sent successfully '''
    json_body = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 200

    assert response.json()["message_id"] == 0

def test_multiple_sent_S_HTTP(clear, user_reg_S, channel_reg_S):
    ''' test multiple messages sent successfully'''
    json_body = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"}
    
    response_1 = requests.post(URL, json = json_body)
    assert response_1.status_code == 200

    response_2 = requests.post(URL, json = json_body)
    assert response_2.status_code == 200
    
    response_3 = requests.post(URL, json = json_body)
    assert response_3.status_code == 200

    response_4 = requests.post(URL, json = json_body)
    assert response_4.status_code == 200

    assert response_1.json()["message_id"] == 0
    assert response_2.json()["message_id"] == 1
    assert response_3.json()["message_id"] == 2
    assert response_4.json()["message_id"] == 3

requests.delete(f"{BASE_URL}/clear/v1", json = {})