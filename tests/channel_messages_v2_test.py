'''
Tests for channel_messaegs_v2. i.e. http wrap of channel_messages from iteration 1.
'''

import pytest
import requests
from src import config
from src.tokens import *

BASE_URL = config.url


valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
another_valid_user = {"email": "anothervalid@email.com", "password": "anotherpassword", "name_first": "firstname", "name_last": "lastname"}

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})


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


def test_invalid_user(clear):
    ''' invalid token (and channel but AccessError has higher priority)'''
    response = requests.get(f"{BASE_URL}/channel/messages/v2?token=invalidtoken&channel_id=3&start=0")
    assert response.status_code == 403 

def test_invalid_channel(clear, user_reg_S):
    ''' invalid channel_id (valid token now)'''
    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S}&channel_id=3&start=0")
    assert response.status_code == 400

def test_start_number_too_big(clear, user_reg_S, channel_reg_S):
    ''' currently have 0 messages right now, so 10 > 0'''
    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S}&channel_id={channel_reg_S}&start=10")
    assert response.status_code == 400

def test_valid_but_no_messages(clear, user_reg_S, channel_reg_S):
    ''' test valid but no messages'''
    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S}&channel_id={channel_reg_S}&start=0")
    assert response.status_code == 200

    response_data = response.json()
    assert response_data == {"messages": [], "start": 0, "end": -1}

def test_auth_user_non_member(clear, user_reg_S, channel_reg_S, another_user_reg_S):
    ''' test token used to call route is not actually in the channel'''
    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={another_user_reg_S}&channel_id={channel_reg_S}&start=0")
    assert response.status_code == 403

def test_over_fifty_messages(clear, user_reg_S, channel_reg_S):
    ''' test when over 50 messages are sent to a channel'''
    for i in range(51):
        requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": str(-i)})
    response = requests.get(f"{BASE_URL}/channel/messages/v2?token={user_reg_S}&channel_id={channel_reg_S}&start=0")

    message_list = response.json()["messages"]
    assert len(message_list) == 50
    for i in range(50):
        assert message_list[i]["message_id"] == 50 - i
        assert message_list[i]["message"] == str(i - 50)

    requests.delete(f"{BASE_URL}/clear/v1", json = {})



