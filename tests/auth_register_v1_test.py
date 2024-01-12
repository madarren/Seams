'''
Tests for auth_register_v1.

'''
import pytest
from src.data_store import initial_object
from src.auth import auth_register_v1
from src.error import InputError
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

def test_invalid_email(clear):
    ''' Test invalid email raises InputError. '''
    with pytest.raises(InputError):
        auth_register_v1('invalidemail', 'password', 'firstname', 'lastname')

def test_duplicate_email(clear):
    ''' Test duplicate email raises InputError. '''
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    with pytest.raises(InputError):
        auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')

def test_invalid_password(clear):
    ''' Test invalid password raises InputError. '''
    with pytest.raises(InputError):
        auth_register_v1('valid@email.com', '12345', 'firstname', 'lastname')

def test_invalid_short_first_name(clear):
    ''' Test short first name raises InputError. '''
    with pytest.raises(InputError):
        auth_register_v1('valid@email.com', 'password', '', 'lastname')

def test_invalid_long_first_name(clear):
    ''' Test long first name raises InputError. '''
    with pytest.raises(InputError):
        auth_register_v1('valid@email.com', 'password', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz', 'lastname')

def test_invalid_short_last_name(clear):
    ''' Test short last name raises InputError. '''
    with pytest.raises(InputError):
        auth_register_v1('valid@email.com', 'password', 'firstname', '')

def test_invalid_long_last_name(clear):
    ''' Test long last name raises InputError. '''
    with pytest.raises(InputError):
        auth_register_v1('valid@email.com', 'password', 'firstname', 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz')

def test_valid_id_generated(clear):
    ''' Test that when valid users are created, correct token and ids returned. '''
    first_id = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    second_id = auth_register_v1('second@email.com', 'password', 'firstname1', 'lastname')
    assert first_id == {'token': initial_object['tokens'][0], 'auth_user_id': 1,}
    assert second_id == {'token': initial_object['tokens'][1],'auth_user_id': 2,}

def test_handle_lowercase_alphanumeric(clear):
    ''' Check correct handles are made of lowercase alphanumeric. '''
    auth_register_v1('valid@email.com', 'password', 'Firstname123', 'Lastname!!')
    first_user = initial_object['users'][0]
    handle_check = first_user['handle']
    assert handle_check == "firstname123lastname"

def test_handle_length(clear):
    ''' Check handle length is correct by being max 20 characters (no duplicates). '''
    auth_register_v1('valid@email.com', 'password', 'firstname12345', 'lastname')
    first_user = initial_object['users'][0]
    handle_check = first_user['handle']
    assert handle_check == "firstname12345lastna"

def test_handle_duplicate(clear):
    ''' Check duplicate handles are correctly named. '''
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    auth_register_v1('second@email.com', 'password', 'firstname', 'lastname')
    auth_register_v1('third@email.com', 'password', 'firstname', 'lastname')
    second_user, third_user = initial_object['users'][1], initial_object['users'][2]
    handle_second, handle_third = second_user['handle'], third_user['handle']
    assert handle_second == "firstnamelastname0"
    assert handle_third == "firstnamelastname1"

def test_handle_length_duplicate(clear):
    ''' Check duplicate handles have correct length. '''
    auth_register_v1('valid@email.com', 'password', 'firstname12345', 'lastname')
    auth_register_v1('second@email.com', 'password', 'firstname12345', 'lastname')
    second_user = initial_object['users'][1]
    handle_second = second_user['handle']
    assert handle_second == "firstname12345lastna0"

def test_global_owner_global_member(clear):
    ''' Check correct global permissions are assigned. '''
    auth_register_v1('valid@email.com', 'password', 'firstname12345', 'lastname')
    auth_register_v1('second@email.com', 'password', 'firstname12345', 'lastname')
    first_user, second_user = initial_object['users'][0], initial_object['users'][1]
    assert first_user['global_permission'] == 1
    assert second_user['global_permission'] == 2

clear_v1()
