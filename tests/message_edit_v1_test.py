'''
This file contains tests for the implementation of message_edit_v1 and its http wrap.

'''

import pytest
from src.message import message_send_v1, message_edit_v1
from src.error import AccessError, InputError 
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
import requests
from src import config

import string 
import random

BASE_URL = config.url
URL = BASE_URL + "/message/edit/v1"

valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
another_valid_user = {"email": "anothervalid@email.com", "password": "anotherpassword", "name_first": "firstname", "name_last": "lastname"}


@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
    clear_v1()

@pytest.fixture
def user_reg_S_B():
    return auth_register_v1("valid@email.com", "password", "namefirst", "namelast")['token']

@pytest.fixture
def user_reg_S_HTTP():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()["token"]

@pytest.fixture
def another_user_reg_S_B():
    return auth_register_v1("anothervalid@email.com", "password", "namefirst", "namelast")['token']

@pytest.fixture
def another_user_reg_S_HTTP():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)
    return response.json()["token"]

@pytest.fixture
def channel_reg_S_B(user_reg_S_B):
    return channels_create_v1(user_reg_S_B, "Channel 1", True)["channel_id"]

@pytest.fixture 
def channel_reg_S_HTTP(user_reg_S_HTTP):
    json_body = {"token": user_reg_S_HTTP, "name": "channel 1", "is_public": True}
    return requests.post(f"{BASE_URL}/channels/create/v2", json = json_body).json()["channel_id"]

@pytest.fixture
def another_channel_reg_S_B(user_reg_S_B):
    return channels_create_v1(user_reg_S_B, "Channel 2", True)["channel_id"]

@pytest.fixture 
def another_channel_reg_S_HTTP(user_reg_S_HTTP):
    json_body = {"token": user_reg_S_HTTP, "name": "channel 2", "is_public": True}
    return requests.post(f"{BASE_URL}/channels/create/v2", json = json_body).json()["channel_id"]

def test_invalid_user_B(clear):
    ''' invalid token (and message_id but AccessError has higher priority)'''
    with pytest.raises(AccessError):
        message_edit_v1("invalidtoken", 3, "Hello World")


def test_invalid_user_HTTP(clear):
    ''' invalid token (and channel but AccessError has higher priority)'''
    json_body = {"token": "invalidtoken", "message_id": 3, "message": "Hello World"}
    response = requests.put(URL, json = json_body)
    assert response.status_code == 403 


def test_invalid_message_id_B(clear, user_reg_S_B):
    ''' invalid message_id (valid token now)'''
    with pytest.raises(InputError):
        message_edit_v1(user_reg_S_B, 3, "Hello World")


def test_invalid_message_id_HTTP(clear, user_reg_S_HTTP):
    ''' invalid message_id (valid token now)'''
    json_body = {"token": user_reg_S_HTTP, "message_id": 3, "message": "Hello World"}
    response = requests.put(URL, json = json_body)
    assert response.status_code == 400

def test_message_too_long_B(clear, user_reg_S_B, channel_reg_S_B):
    ''' message exceeds 1000 characters'''
    message_id = message_send_v1(user_reg_S_B, channel_reg_S_B, "Hello World")["message_id"]
    long_message = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    with pytest.raises(InputError):
        message_edit_v1(user_reg_S_B, message_id, long_message)

def test_message_too_long_HTTP(clear, user_reg_S_HTTP, channel_reg_S_HTTP):
    ''' message exceeds 1000 characters'''
    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "message": "Hello World"}
    response = requests.post(f"{BASE_URL}/message/send/v1", json = json_body)

    long_message = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    json_body = {"token": user_reg_S_HTTP, "message_id": response.json()["message_id"], "message": long_message}
    response = requests.put(URL, json = json_body)
    assert response.status_code == 400

def test_empty_message_B(clear, user_reg_S_B, channel_reg_S_B):
    ''' message is 0 chars (empty)'''
    message_id = message_send_v1(user_reg_S_B, channel_reg_S_B, "Hello World")["message_id"]
    message_edit_v1(user_reg_S_B, message_id, "")
    assert channel_messages_v1(user_reg_S_B, channel_reg_S_B, 0)["messages"] == []

def test_empty_message_HTTP(clear, user_reg_S_HTTP, channel_reg_S_HTTP):
    ''' message is 0 chars (empty)'''
    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "message": "Hello World"}
    response = requests.post(f"{BASE_URL}/message/send/v1", json = json_body)

    json_body = {"token": user_reg_S_HTTP, "message_id": response.json()["message_id"], "message": ""}
    response = requests.put(URL, json = json_body)
    assert response.status_code == 200
    
    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S_HTTP}&channel_id={channel_reg_S_HTTP}&start=0")
    assert response.json()["messages"] == []
    assert response.status_code == 200

def test_valid_message_id_no_auth_B(clear, user_reg_S_B, channel_reg_S_B, another_user_reg_S_B):
    ''' the message id is valid but since the id is not in a channel the user is in (the user is not in any channels), raise input error'''
    message_id = message_send_v1(user_reg_S_B, channel_reg_S_B, "Hello World")["message_id"]
    with pytest.raises(InputError):
        message_edit_v1(another_user_reg_S_B, message_id, "Hello")

def test_valid_message_id_no_auth_HTTP(clear, user_reg_S_HTTP, channel_reg_S_HTTP, another_user_reg_S_HTTP):
    ''' the message id is valid but since the id is not in a channel the user is in (the user is not in any channels), raise input error'''
    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]

    json_body = {"token": another_user_reg_S_HTTP, "message_id": message_id, "message": "Hello"}
    response = requests.put(URL, json = json_body)
    assert response.status_code == 400

def test_valid_edit_B(clear, user_reg_S_B, channel_reg_S_B):
    ''' valid edit '''
    message_id = message_send_v1(user_reg_S_B, channel_reg_S_B, "Hello World")["message_id"]
    message_edit_v1(user_reg_S_B, message_id, "Hello")
    assert channel_messages_v1(user_reg_S_B, channel_reg_S_B, 0)["messages"][0]["message"] == "Hello"

def test_valid_edit_HTTP(clear, user_reg_S_HTTP, channel_reg_S_HTTP):
    ''' valid edit '''
    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]
    
    json_body = {"token": user_reg_S_HTTP, "message_id": message_id, "message": "Hello"}
    requests.put(URL, json = json_body)

    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S_HTTP}&channel_id={channel_reg_S_HTTP}&start=0")
    assert response.json()["messages"][0]["message"] == "Hello"
    assert response.status_code == 200

def test_multiple_edit_B(clear, user_reg_S_B, channel_reg_S_B):
    ''' valid edit '''
    message_send_v1(user_reg_S_B, channel_reg_S_B, "Hello World")["message_id"]
    message_id_2 = message_send_v1(user_reg_S_B, channel_reg_S_B, "Hello")["message_id"]
    message_edit_v1(user_reg_S_B, message_id_2, "Hellooooooooo")
    assert channel_messages_v1(user_reg_S_B, channel_reg_S_B, 0)["messages"][0]["message"] == "Hellooooooooo"
    assert channel_messages_v1(user_reg_S_B, channel_reg_S_B, 0)["messages"][1]["message"] == "Hello World"
    
def test_multiple_edit_HTTP(clear, user_reg_S_HTTP, channel_reg_S_HTTP):
    ''' valid edit '''
    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "message": "Hello World"}
    requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]
    
    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "message": "Hello"}
    message_id_2 = requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]

    json_body = {"token": user_reg_S_HTTP, "message_id": message_id_2, "message": "Hellooooooooo"}
    requests.put(URL, json = json_body)

    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S_HTTP}&channel_id={channel_reg_S_HTTP}&start=0")
    assert response.json()["messages"][0]["message"] == "Hellooooooooo"
    assert response.json()["messages"][1]["message"] == "Hello World"

    assert response.status_code == 200

def test_multiple_channel_edit_B(clear, user_reg_S_B, channel_reg_S_B, another_channel_reg_S_B):
    ''' valid edit '''
    message_id = message_send_v1(user_reg_S_B, another_channel_reg_S_B, "Hello World")["message_id"]
    message_edit_v1(user_reg_S_B, message_id, "Hello")
    assert channel_messages_v1(user_reg_S_B, another_channel_reg_S_B, 0)["messages"][0]["message"] == "Hello" 

def test_multiple_channel_edit_HTTP(clear, user_reg_S_HTTP, channel_reg_S_HTTP, another_channel_reg_S_HTTP):
    ''' valid edit '''
    json_body = {"token": user_reg_S_HTTP, "channel_id": another_channel_reg_S_HTTP, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]
    
    json_body = {"token": user_reg_S_HTTP, "message_id": message_id, "message": "Hello"}
    requests.put(URL, json = json_body)

    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S_HTTP}&channel_id={another_channel_reg_S_HTTP}&start=0")
    assert response.json()["messages"][0]["message_id"] == message_id
    assert response.json()["messages"][0]["message"] == "Hello"

    assert response.status_code == 200


def test_not_sender_but_owner_edit(clear, user_reg_S_HTTP, channel_reg_S_HTTP):
    ''' owner of channel can edit messages'''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)

    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "u_id": response.json()["auth_user_id"]}
    requests.post(f"{BASE_URL}/channel/invite/v2", json = json_body)

    another_user_reg_S_HTTP = response.json()["token"]
    json_body = {"token": another_user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]

    json_body = {"token": user_reg_S_HTTP, "message_id": message_id, "message": "Hello"}
    requests.put(URL, json = json_body)

    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S_HTTP}&channel_id={channel_reg_S_HTTP}&start=0")
    assert response.json()["messages"][0]["message"] == "Hello" 
    assert response.status_code == 200
    
def test_not_sender_not_owner_edit_channel(clear, user_reg_S_HTTP, channel_reg_S_HTTP):
    ''' a member of the channel that is neither the owner nor the sender cannot edit message'''
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)

    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "u_id": response.json()["auth_user_id"]}
    requests.post(f"{BASE_URL}/channel/invite/v2", json = json_body)

    another_user_reg_S_HTTP = response.json()["token"]
    json_body = {"token": user_reg_S_HTTP, "channel_id": channel_reg_S_HTTP, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]

    json_body = {"token": another_user_reg_S_HTTP, "message_id": message_id, "message": "Hello"}
    response = requests.put(URL, json = json_body)

    assert response.status_code == 403


def test_global_owner_edit_channel(clear):
    ''' a global owner has owner perms of any channel they are in, hence can edit messages'''
    user_1 = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)
    user_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)

    json_body = {"token": user_2.json()["token"], "name": "channel 1", "is_public": True}
    channel_id = requests.post(f"{BASE_URL}/channels/create/v2", json = json_body).json()["channel_id"]

    json_body = {"token": user_2.json()["token"], "channel_id": channel_id, "u_id": user_1.json()["auth_user_id"]}
    requests.post(f"{BASE_URL}/channel/invite/v2", json = json_body)

    json_body = {"token": user_2.json()["token"], "channel_id": channel_id, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/send/v1", json = json_body).json()["message_id"]

    json_body = {"token": user_1.json()["token"], "message_id": message_id, "message": "Hello"}
    response = requests.put(URL, json = json_body)

    assert response.status_code == 200
    
    token_1 = user_1.json()["token"]
    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={token_1}&channel_id={channel_id}&start=0")

    message_list = response.json()["messages"]
    assert message_list[0]["message_id"] == 0
    assert message_list[0]["message"] == "Hello"

    requests.delete(f"{BASE_URL}/clear/v1", json = {})

def test_global_owner_cannot_edit_dm(clear):
    ''' a global owner does not have owner perms of dms they join, hence cannot edit messages'''

    user_1 = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)
    user_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)

    json_body = {'token': user_2.json()["token"],'u_ids': [user_1.json()["auth_user_id"]]}
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = json_body).json()["dm_id"]
    
    json_body = {"token": user_2.json()["token"], "dm_id": dm_id, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/senddm/v1", json = json_body).json()["message_id"]

    json_body = {"token": user_1.json()["token"], "message_id": message_id, "message": "Hello"}
    response = requests.put(URL, json = json_body)

    assert response.status_code == 403


def test_not_sender_but_owner_edit_dm(clear, user_reg_S_HTTP, ):
    ''' owner of dm can edit messages'''
    user_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)

    json_body = {'token': user_reg_S_HTTP,'u_ids': [user_2.json()["auth_user_id"]]}
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = json_body).json()["dm_id"]

    json_body = {"token": user_2.json()["token"], "dm_id": dm_id, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/senddm/v1", json = json_body).json()["message_id"]

    json_body = {"token": user_reg_S_HTTP, "message_id": message_id, "message": "Hello"}
    requests.put(URL, json = json_body)

    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={user_reg_S_HTTP}&dm_id={dm_id}&start=0")
    assert response.json()["messages"][0]["message"] == "Hello" 
    assert response.status_code == 200
    
def test_not_sender_not_owner_edit_dm(clear, user_reg_S_HTTP):
    ''' a member of the channel that is neither the owner nor the sender cannot edit message'''
    
    user_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)

    json_body = {'token': user_reg_S_HTTP,'u_ids': [user_2.json()["auth_user_id"]]}
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = json_body).json()["dm_id"]

    json_body = {"token": user_reg_S_HTTP, "dm_id": dm_id, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/senddm/v1", json = json_body).json()["message_id"]

    json_body = {"token": user_2.json()["token"], "message_id": message_id, "message": "Hello"}
    response = requests.put(URL, json = json_body)

    assert response.status_code == 403

def test_sender_edit_dm(clear, user_reg_S_HTTP):
    ''' a member of the channel that is neither the owner nor the sender cannot edit message'''
    
    user_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user)

    json_body = {'token': user_reg_S_HTTP,'u_ids': [user_2.json()["auth_user_id"]]}
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = json_body).json()["dm_id"]

    json_body = {"token": user_2.json()["token"], "dm_id": dm_id, "message": "Hello World"}
    message_id = requests.post(f"{BASE_URL}/message/senddm/v1", json = json_body).json()["message_id"]

    json_body = {"token": user_2.json()["token"], "message_id": message_id, "message": "Hello"}
    requests.put(URL, json = json_body)

    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={user_reg_S_HTTP}&dm_id={dm_id}&start=0")
    assert response.json()["messages"][0]["message"] == "Hello" 
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json = {})