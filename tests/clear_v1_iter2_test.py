'''
Tests for clear/v1. i.e. http wrap of clear_v1 from iteration 1.

'''

import requests
from src import config

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}

def test_empty_data_store():
    ''' Test that it works on an empty datastore. '''
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200

def test_filled_data_store():
    ''' Test that a datastore with a user is cleared.'''
    requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    response = requests.delete(f"{BASE_URL}/clear/v1")
    assert response.status_code == 200
    duplicate = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert duplicate.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1")
