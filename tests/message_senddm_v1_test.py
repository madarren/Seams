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
URL = BASE_URL + "/message/senddm/v1"

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
def dm_reg_S(user_reg_S):
    json_body = {"token": user_reg_S, "u_ids": []}
    return requests.post(f"{BASE_URL}/dm/create/v1", json = json_body).json()["dm_id"]


def test_invalid_user(clear):
    ''' the user token does not exist, invalid'''
    json_body = {"token": "invalidtoken", "dm_id": -1, "message": "Hello World"}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 403

def test_invalid_dm_id(clear, user_reg_S):
    ''' the dm_id is invalid, does not exist in datastore'''
    json_body = {"token": user_reg_S, "dm_id": -1, "message": "Hello World"}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 400

def test_user_not_in_dm(clear, user_reg_S, another_user_reg_S, dm_reg_S):
    ''' dm_id is valid but auth_user is not in the dm'''
    json_body = {"token": another_user_reg_S, "dm_id": dm_reg_S, "message": "Hello World"}
    response = requests.post(URL, json = json_body)
    response.status_code == 403

def test_message_too_long(clear, user_reg_S, dm_reg_S):
    ''' message exceeds 1000 characters'''
    long_message = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    json_body = {"token": user_reg_S, "dm_id": dm_reg_S, "message": long_message}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 400

def test_message_too_short(clear, user_reg_S, dm_reg_S):
    ''' message exceeds 1000 characters'''
    json_body = {"token": user_reg_S, "dm_id": dm_reg_S, "message": ""}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 400

def test_valid_senddm(clear, user_reg_S, dm_reg_S):
    ''' message_senddm success '''
    json_body = {"token": user_reg_S, "dm_id": dm_reg_S, "message": "Hello World"}
    response = requests.post(URL, json = json_body)
    assert response.status_code == 200
    response = requests.get(f"{BASE_URL}/dm/messages/v1?token={user_reg_S}&dm_id={dm_reg_S}&start=0")
    assert response.json()["messages"][0]["message"] == "Hello World"

    requests.delete(f"{BASE_URL}/clear/v1", json = {})  
