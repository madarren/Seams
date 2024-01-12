'''
This file contains tests for the implementation of admin_userpermission_change_v1 and its http wrap

'''
import pytest
from src.user import admin_userpermission_change_v1
from src.error import InputError, AccessError
from src.other import clear_v1, get_permission
from src.auth import auth_register_v1
import requests
from src import config

BASE_URL = config.url

@pytest.fixture
def clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
    clear_v1()

@pytest.fixture
def new_user_backend():
    return auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')

@pytest.fixture
def backend_user2():
    return auth_register_v1('second@email.com', 'password', 'first', 'last')

@pytest.fixture
def new_user_frontend():
    valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()

@pytest.fixture
def frontend_user2():
    valid_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'first', 'name_last': 'last'}
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    return response.json()


def test_invalid_token_backend(clear):
    ''' Test that the backend implementation raises AccessError for invalid token. '''
    with pytest.raises(AccessError):
        admin_userpermission_change_v1("token", 1, 1)

def test_invalid_token_frontend(clear):
    ''' Test that the frontend raises AccessError for invalid token. '''
    json_data = {'token': 'token', 'u_id': 1, 'permission_id': 1}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 403

def test_auth_user_not_global_owner_backend(clear, new_user_backend, backend_user2):
    ''' Test backend raises AccessError when auth user is to a global owner. '''
    with pytest.raises(AccessError):
        admin_userpermission_change_v1(backend_user2['token'], 1, 1)

def test_auth_user_not_global_owner_frontend(clear, new_user_frontend, frontend_user2):
    ''' Test frontend raises AccessError when auth user is to a global owner. '''
    json_data = {'token': frontend_user2['token'], 'u_id': 1, 'permission_id': 1}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 403

def test_invalid_u_id_backend(clear, new_user_backend):
    ''' Test that backend raises InputError when u_id is invalid. '''
    with pytest.raises(InputError):
        admin_userpermission_change_v1(new_user_backend['token'], 99, 2)

def test_invalid_u_id_frontend(clear, new_user_frontend):
    ''' Test frontend raises InputError when u_id is invalid. '''
    json_data = {'token': new_user_frontend['token'], 'u_id':99, 'permission_id': 2}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 400

def test_one_global_owner_demote_backend(clear, new_user_backend):
    ''' Test that backend raises InputError when demoting the only global owner. '''
    with pytest.raises(InputError):
        admin_userpermission_change_v1(new_user_backend['token'], new_user_backend['auth_user_id'], 2)

def test_one_global_owner_demote_frontend(clear, new_user_frontend):
    ''' Test frontend raises InputError when demoting the only global owner. '''
    json_data = {'token': new_user_frontend['token'], 'u_id': new_user_frontend['auth_user_id'], 'permission_id': 2}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 400

def test_invalid_permission_id_backend(clear, new_user_backend, backend_user2):
    ''' Test backend raises InputError when permission_id is not valid. '''
    with pytest.raises(InputError):
        admin_userpermission_change_v1(new_user_backend['token'], backend_user2['auth_user_id'], 0)

def test_invalid_permission_id_frontend(clear, new_user_frontend, frontend_user2):
    ''' Test frontend raises InputError when permission_id is not valid. '''
    json_data = {'token': new_user_frontend['token'], 'u_id': frontend_user2['auth_user_id'], 'permission_id': 0}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 400
    json_data = {'token': new_user_frontend['token'], 'u_id': new_user_frontend['auth_user_id'], 'permission_id': 99}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 400

def test_same_permission_id_2_backend(clear, new_user_backend, backend_user2):
    ''' Test backend raises InputError when permission_id is the same as before (user). '''
    with pytest.raises(InputError):
        admin_userpermission_change_v1(new_user_backend['token'], backend_user2['auth_user_id'], 2)

def test_same_permission_id_2_frontend(clear, new_user_frontend, frontend_user2):
    ''' Test frontend raises InputError when permission_id is the same as before (user). '''
    json_data = {'token': new_user_frontend['token'], 'u_id': frontend_user2['auth_user_id'], 'permission_id': 2}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 400

def test_promote_user_backend(clear, new_user_backend, backend_user2):
    ''' Test can promote a user to owner in the backend. '''
    admin_userpermission_change_v1(new_user_backend['token'], backend_user2['auth_user_id'], 1)
    assert get_permission(backend_user2['auth_user_id']) == 1

def test_promote_user_frontend(clear, new_user_frontend, frontend_user2):
    ''' Test can promote a user to owner in the frontend. '''
    json_data = {'token': new_user_frontend['token'], 'u_id': frontend_user2['auth_user_id'], 'permission_id': 1}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 200

def test_can_demote_owner_backend(clear, new_user_backend, backend_user2):
    ''' Test can demote an owner to user in the backend. '''
    admin_userpermission_change_v1(new_user_backend['token'], backend_user2['auth_user_id'], 1)
    admin_userpermission_change_v1(backend_user2['token'], new_user_backend['auth_user_id'], 2)
    assert get_permission(backend_user2['auth_user_id']) == 1

def test_can_demote_owner_frontend(clear, new_user_frontend, frontend_user2):
    ''' Test can demote an owner to user in the frontend. '''
    json_prom = {'token': new_user_frontend['token'], 'u_id': frontend_user2['auth_user_id'], 'permission_id': 1}
    requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_prom)
    json_demo = {'token': frontend_user2['token'], 'u_id': new_user_frontend['auth_user_id'], 'permission_id': 2}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_demo)
    assert response.status_code == 200
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_demo)
    assert response.status_code == 400

def test_same_permission_id_1_backend(clear, new_user_backend, backend_user2):
    ''' Test backend raises InputError when permission_id is the same as before (owner). '''
    admin_userpermission_change_v1(new_user_backend['token'], backend_user2['auth_user_id'], 1)
    with pytest.raises(InputError):
        admin_userpermission_change_v1(new_user_backend['token'], backend_user2['auth_user_id'], 1)

def test_same_permission_id_1_frontend(clear, new_user_frontend, frontend_user2):
    ''' Test frontend raises InputError when permission_id is the same as before (owner). '''
    json_data = {'token': new_user_frontend['token'], 'u_id': frontend_user2['auth_user_id'], 'permission_id': 1}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    json_data = {'token': new_user_frontend['token'], 'u_id': frontend_user2['auth_user_id'], 'permission_id': 1}
    response = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json = json_data)
    assert response.status_code == 400

requests.delete(f"{BASE_URL}/clear/v1", json = {})
clear_v1()
