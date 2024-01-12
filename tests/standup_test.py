'''
Test file for standup_start_v1, standup_active_v1 and standup_send_v1
'''

import pytest
import time 
import string
import random
import requests
import threading
from datetime import datetime, timedelta
from src.data_store import initial_object 
from src.error import InputError, AccessError
from src.channel import *
from src.channels import *
from src.other import clear_v1
from src.auth import *
from src.tokens import *
from src.standup import *
from src import config

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'joel', 'name_last': 'embiid'}
valid3_user = {'email': 'raccooncity@city.co', 'password': 'S.T.A.R.S', 'name_first': 'Leon', 'name_last': 'Kennedy'}

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_reg_S():
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    data = auth_login_v1('valid@email.com', 'password')
    return data

@pytest.fixture
def H_clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def H_user_reg_S():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def H_user_reg_S2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def length():
    return 0.05

def test_standup(clear, user_reg_S):
    '''
    Test case for successful standup
    '''
    u_token = user_reg_S['token']
    c_dict = channels_create_v1(u_token, 'SeamEgg', True)
    c_id = c_dict["channel_id"]

    length = 0.05
    standup_start_v1(u_token, c_id, length)
    standup_send_v1(u_token, c_id, "Standing")
    time.sleep(0.1)
    messages = initial_object["channels"][c_id]["message"]
    assert messages[0]["message"] == "firstnamelastname: Standing\n"

def test_standup_start_invalid_token(H_clear, H_user_reg_S, length):
    '''
    Test if Accesserror is raised when invalid token
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": "Undefined", "channel_id": c_id, "length": length})
    assert response.status_code == 403

def test_standup_start_nonmember(H_clear, H_user_reg_S, H_user_reg_S2, length):
    '''
    Test if Accesserror is raised when user is not in the channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "length": length})
    assert response.status_code == 403

def test_standup_start_invalid_cid(H_clear, H_user_reg_S, length):
    '''
    Test if Inputerror is raised if the channel ID is invalid
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": 88888888, "length": length})
    assert response.status_code == 400

def test_standup_start_invalid_length(H_clear, H_user_reg_S):
    '''
    Test if Inputerror is raised if the length of standup is set as negative
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": -1})
    assert response.status_code == 400

def test_standup_start_doubled(H_clear, H_user_reg_S, length):
    '''
    Test if Inputerror is raised when another standup is active
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": length})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": length})
    assert response.status_code == 400


#############################################################################################################

def test_standup_active_invalid_token(H_clear, H_user_reg_S):
    '''
    Test if Accesserror is raised when invalid token
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    token = "Undefined"

    response = requests.get(
        f"{BASE_URL}/standup/active/v1?token={token}&channel_id={c_id}")
    assert response.status_code == 403

def test_standup_active_nonmember(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test if Accesserror is raised when user is not in the channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.get(
        f"{BASE_URL}/standup/active/v1?token={H_user_reg_S2['token']}&channel_id={c_id}")
    assert response.status_code == 403

def test_standup_active_invalid_cid(H_clear, H_user_reg_S):
    '''
    Test if Inputerror is raised if the channel ID is invalid
    '''
    c_id = 88888888
    response = requests.get(
        f"{BASE_URL}/standup/active/v1?token={H_user_reg_S['token']}&channel_id={c_id}")
    assert response.status_code == 400


##################################################################################################################

def test_standup_send_invalid_token(H_clear, H_user_reg_S, length):
    '''
    Test if Accesserror is raised when invalid token
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": length})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": "Undefined", "channel_id": c_id, "message": "Chris: Wash apple till night"})
    assert response.status_code == 403

def test_standup_send_nonmember(H_clear, H_user_reg_S, H_user_reg_S2, length):
    '''
    Test if Accesserror is raised when user is not in the channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": length})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "message": "Chris: Wash apple till night"})
    assert response.status_code == 403

def test_standup_send_invalid_cid(H_clear, H_user_reg_S, length):
    '''
    Test if Inputerror is raised if the channel ID is invalid
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']
    
    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": length})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S['token'], "channel_id": 88888888, "message": "Chris: Wash apple till night"})
    assert response.status_code == 400

def test_standup_send_message_too_long(H_clear, H_user_reg_S, length):
    '''
    Test if Inputerror is raised when the message length is longer than 1000
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": length})
    assert response.status_code == 200

    long_message = ''.join(random.choice(string.ascii_letters) for _ in range(1001))
    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "message": long_message})
    assert response.status_code == 400

def test_standup_send_not_active(H_clear, H_user_reg_S, length):
    '''
    Test if Inputerror is raised when the standup is not active
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": length})
    assert response.status_code == 200
    time.sleep(0.75)

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "message": "Chris: Wash apple till night"})
    assert response.status_code == 400

######################################################################################################################

def test_standup_1(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Successful case for all standup function. (Public)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    length = 1
    requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "length": length})

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "message": "Pick apple till night"})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "message": "Wash apple till night"})
    assert response.status_code == 200

    response = requests.get(
        f"{BASE_URL}/standup/active/v1?token={H_user_reg_S['token']}&channel_id={c_id}")
    assert response.status_code == 200
    standup_data = response.json()
    assert standup_data['is_active'] == True
    assert standup_data['time_finish'] < (datetime.now()+timedelta(seconds=length)).timestamp()
    time.sleep(2)

    response = requests.get(
        f"{BASE_URL}/standup/active/v1?token={H_user_reg_S['token']}&channel_id={c_id}")
    assert response.status_code == 200
    standup_data = response.json()
    assert standup_data['is_active'] == False
    assert standup_data['time_finish'] == None

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "message": "Eat apple till night"})
    assert response.status_code == 400


def test_standup_2(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Successful case for all standup function. (Private)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Egg", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200

    length = 1
    requests.post(
        f"{BASE_URL}/standup/start/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "length": length})

    response = requests.get(
        f"{BASE_URL}/standup/active/v1?token={H_user_reg_S2['token']}&channel_id={c_id}")
    assert response.status_code == 200
    standup_data = response.json()
    assert standup_data['is_active'] == True
    assert standup_data['time_finish'] < (datetime.now()+timedelta(seconds=length)).timestamp()

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "message": "Wash egg till day"})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "message": "Cook egg till day"})
    assert response.status_code == 200
    time.sleep(2)

    response = requests.get(
        f"{BASE_URL}/standup/active/v1?token={H_user_reg_S['token']}&channel_id={c_id}")
    assert response.status_code == 200
    standup_data = response.json()
    assert standup_data['is_active'] == False
    assert standup_data['time_finish'] == None

    response = requests.post(
        f"{BASE_URL}/standup/send/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "message": "Eat apple till night"})
    assert response.status_code == 400


    requests.delete(f"{BASE_URL}/clear/v1", json = {})

