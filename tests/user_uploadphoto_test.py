'''
This file contains tests for the implementation of user profile uploadphoto and its http wrap.
'''
import pytest
import requests
from src import config

BASE_URL = config.url
PHOTO_URL = 'https://research.unsw.edu.au/sites/default/files/styles/profile/public/images/profile/richard%20b%20profile_0.jpeg'
PNG_URL = 'https://www.pngitem.com/pimgs/m/79-791921_male-profile-round-circle-users-profile-round-icon.png'

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def new_user():
    valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()


def test_invalid_token(clear):
    ''' Test the function raises AccessError for invalid token. '''
    json_data = {'token': 'token', 'img_url': 'thisisurl', 'x_start': 1, 'y_start': 1, 'x_end': 100, 'y_end': 100}
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json = json_data)
    assert response.status_code == 403

def test_invalid_photo_url(clear, new_user):
    ''' Test InputError raised when an invalid url is given. '''
    json_data = {'token': new_user['token'], 'img_url': 'http://nophoto', 'x_start': 1, 'y_start': 1, 'x_end': 100, 'y_end': 100}
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json = json_data)
    assert response.status_code == 400
    json_data = {'token': new_user['token'], 'img_url': PNG_URL, 'x_start': 1, 'y_start': 1, 'x_end': 100, 'y_end': 100}
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json = json_data)
    assert response.status_code == 400

def test_invalid_photo_dimensions(clear, new_user):
    ''' Test InputError raised when size dimensions are invalid. '''
    json_data = {'token': new_user['token'], 'img_url': PHOTO_URL, 'x_start': -1, 'y_start': 1, 'x_end': 100, 'y_end': 100}
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json = json_data)
    assert response.status_code == 400
    json_data = {'token': new_user['token'], 'img_url': PHOTO_URL, 'x_start': 1, 'y_start': -1, 'x_end': 100, 'y_end': 100}
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json = json_data)
    assert response.status_code == 400
    json_data = {'token': new_user['token'], 'img_url': PHOTO_URL, 'x_start': 10, 'y_start': 1, 'x_end': 9, 'y_end': 100}
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json = json_data)
    assert response.status_code == 400
    json_data = {'token': new_user['token'], 'img_url': PHOTO_URL, 'x_start': 1, 'y_start': 1, 'x_end': 10000, 'y_end': 10000}
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json = json_data)
    assert response.status_code == 400

def test_valid_upload(clear, new_user):
    ''' Test a photo can be uploaded. '''
    json_data = {'token': new_user['token'], 'img_url': PHOTO_URL, 'x_start': 1, 'y_start': 1, 'x_end': 100, 'y_end': 100}
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json = json_data)
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
