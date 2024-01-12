'''
Tests for auth_login_v1
'''
import pytest 

from src.data_store import initial_object
from src.auth import auth_register_v1, auth_login_v1 
from src.error import InputError
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

def test_no_registered_users(clear):
    '''
    No registered users yet
    Note: email is valid 
    '''
    with pytest.raises(InputError):
        auth_login_v1("valid@email.com", "password")

def test_wrong_registered_email(clear):
    ''' Login with a valid email that is not yet registered. Data store does contain an email '''
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    with pytest.raises(InputError):
        auth_login_v1("wrongvalid@email.com", "password")

def test_successful_login(clear):
    ''' test successful login'''
    reg_user_id = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    login_user_id = auth_login_v1("valid@email.com", "password")
    assert login_user_id['auth_user_id'] == reg_user_id['auth_user_id']

def test_incorrect_password(clear):
    ''' email used to login matches one in database, but password is incorrect '''
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    with pytest.raises(InputError):
        auth_login_v1("valid@email.com", "wrongpassword")
    
def test_multiple_successful_login(clear):
    ''' Testing when multiple users login '''
    reg_user_id1 = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    reg_user_id2 = auth_register_v1("anothervalid@email.com", "anotherpassword", "differentfirstname", "differentlastname")

    login_user_id1 = auth_login_v1("valid@email.com", "password")
    login_user_id2 = auth_login_v1("anothervalid@email.com", "anotherpassword")

    assert reg_user_id1['auth_user_id'] == login_user_id1['auth_user_id']
    assert reg_user_id2['auth_user_id'] == login_user_id2['auth_user_id']

clear_v1()
