'''
    Tests for message/pin/v1 and message/unpin/v1
'''

import pytest
import requests
from src import config

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
    return response.json()

@pytest.fixture 
def channel_reg_S(user_reg_S):
    json_body = {"token": user_reg_S, "name": "channel 1", "is_public": True}
    return requests.post(f"{BASE_URL}/channels/create/v2", json = json_body).json()["channel_id"]


'''
Tests for pin and unpin will be distinguished by P/UP suffix
'''

def test_invalid_user_P(clear):
    ''' invalid token (and channel but AccessError has higher priority)'''
    json_body = {"token": "invalidtoken", "message_id": 3}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 403 

def test_invalid_user_UP(clear):
    ''' invalid token'''
    json_body = {"token": "invalidtoken", "message_id": 3}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 403

def test_invalid_message_id_P(clear, user_reg_S):
    ''' invalid message id'''
    json_body = {"token": user_reg_S, "message_id": 3}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 400

def test_invalid_message_id_UP(clear, user_reg_S):
    ''' invalid messagae id'''
    json_body = {"token": user_reg_S, "message_id": 3, "react_id": 1}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 400

def test_user_not_in_channel_P(clear, user_reg_S, another_user_reg_S, channel_reg_S):
    ''' valid message id but auth user is not in channel'''
    token = another_user_reg_S["token"]
    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"})
    json_body = {"token": token, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 400

def test_user_not_in_channel_UP(clear, user_reg_S, another_user_reg_S, channel_reg_S):
    ''' valid message id but auth user is not in channel'''
    token = another_user_reg_S["token"]
    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"})
    json_body = {"token": token, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 400

def test_user_no_owner_perms_P(clear, user_reg_S, another_user_reg_S, channel_reg_S):
    json_body = {"token": user_reg_S, "channel_id": channel_reg_S, "u_id": another_user_reg_S["auth_user_id"]}
    requests.post(f"{BASE_URL}/channel/invite/v2", json = json_body)

    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": another_user_reg_S["token"], "channel_id": channel_reg_S, "message": "Hello World"})
    json_body = {"token": another_user_reg_S["token"], "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 403

def test_user_no_owner_perms_UP(clear, user_reg_S, another_user_reg_S, channel_reg_S):
    json_body = {"token": user_reg_S, "channel_id": channel_reg_S, "u_id": another_user_reg_S["auth_user_id"]}
    requests.post(f"{BASE_URL}/channel/invite/v2", json = json_body)

    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": another_user_reg_S["token"], "channel_id": channel_reg_S, "message": "Hello World"})
    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": another_user_reg_S["token"], "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 403

def test_already_reacted_R(clear, user_reg_S, channel_reg_S):
    ''' invalid react id '''
    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"})
    
    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 400

def test_not_yet_reacted_UR(clear, user_reg_S, channel_reg_S):
    ''' invalid react id'''
    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"})
    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 400


def test_valid_P_UP(clear, user_reg_S, channel_reg_S):
    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"})
    
    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 200

def test_valid_multiple_message_P_UP(clear, user_reg_S, another_user_reg_S, channel_reg_S):
    
    json_body = {"token": user_reg_S, "channel_id": channel_reg_S, "u_id": another_user_reg_S["auth_user_id"]}
    requests.post(f"{BASE_URL}/channel/invite/v2", json = json_body)
    
    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello World"})
    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "Hello"})
    requests.post(f"{BASE_URL}/message/send/v1", json = {"token": user_reg_S, "channel_id": channel_reg_S, "message": "HELLO WORLD"})


    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 1}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 2}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 1}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 200


def test_valid_multiple_message_dm_P_UP(clear, user_reg_S, another_user_reg_S):
    
    json_body = {'token': user_reg_S,'u_ids': [another_user_reg_S["auth_user_id"]]}
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = json_body).json()["dm_id"]
    
    requests.post(f"{BASE_URL}/message/senddm/v1", json = {"token": user_reg_S, "dm_id": dm_id, "message": "Hello World"})
    requests.post(f"{BASE_URL}/message/senddm/v1", json = {"token": user_reg_S, "dm_id": dm_id, "message": "Hello"})
    requests.post(f"{BASE_URL}/message/senddm/v1", json = {"token": user_reg_S, "dm_id": dm_id, "message": "HELLO WORLD"})


    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 1}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 2}
    response = requests.post(f"{BASE_URL}/message/pin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 0}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 200

    json_body = {"token": user_reg_S, "message_id": 1}
    response = requests.post(f"{BASE_URL}/message/unpin/v1", json = json_body)
    assert response.status_code == 200
    
    requests.delete(f"{BASE_URL}/clear/v1", json = {})