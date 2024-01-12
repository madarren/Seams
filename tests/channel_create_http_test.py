'''
Test file for channel/create/v2 (http)
'''

import pytest
import requests
from src import config
from src.tokens import *

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


def test_create_channel_public(clear, user_reg_S):
    '''
    Success case for create multiple channels with correct channel ID (Public)
    '''

    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S, "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()
    assert c_id['channel_id'] == 0
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S, "name": "Seam_Banana", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()
    assert c_id['channel_id'] == 1

def test_create_channel_public_fail(clear, user_reg_S):
    '''
    Test if Inputerror is raised when the channel name is too long
    '''

    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={
            "token": user_reg_S, "name": "GroupofMonkeysDancingTogether", "is_public": True})
    assert response.status_code == 400

def test_create_channel_private(clear, user_reg_S):
    '''
    Success case for create multiple channels with correct channel ID (Private)
    '''

    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S, "name": "Seam_Apple", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()
    assert c_id['channel_id'] == 0
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": user_reg_S, "name": "Seam_Banana", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()
    assert c_id['channel_id'] == 1

def test_create_channel_private_fail(clear, user_reg_S):
    '''
    Test if Inputerror is raised when the channel name is too long
    '''

    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={
            "token": user_reg_S, "name": "GroupofMonkeysDancingTogether", "is_public": False})
    assert response.status_code == 400

def test_bad_request(clear, user_reg_S):
    '''
    Test for no input
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={})
    assert response.status_code == 500

def test_channel_create_invalid_token(clear):
    '''
    Test if Accesserror is raised when token is not valid
    '''
    json_data = {'email': '', 'password': '', 'name_first': '', 'name_last': ''}
    response = requests.post(
        f"{BASE_URL}/auth/register/v2", json = json_data)
    assert response.status_code == 400

    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": "Undefined", "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 403

def test_channel_create_no_token(clear):
    '''
    Test if Accesserror is raised when there is no token
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": "", "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 403

requests.delete(f"{BASE_URL}/clear/v1", json = {})