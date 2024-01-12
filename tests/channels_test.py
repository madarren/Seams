import pytest

from src.channels import channels_create_v1
from src.auth import auth_register_v1, auth_login_v1
from src.data_store import initial_object
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def clear():
    clear_v1()

# Successful registration
@pytest.fixture
def user_reg_S():
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    data = auth_login_v1('valid@email.com', 'password')
    return data['token']


def test_channel_create_public_success(clear, user_reg_S):
    '''
    Success case for create multiple channels with correct channel ID (Public)
    '''
    user_id = user_reg_S

    c_id = channels_create_v1(user_id, 'SeamApple', True)
    assert c_id == {'channel_id': 0}
    c_id = channels_create_v1(user_id, 'SeamCoal', True)
    assert c_id == {'channel_id': 1}
    c_id = channels_create_v1(user_id, 'SeamDinner', True)
    assert c_id == {'channel_id': 2}

def test_channel_create_public(clear, user_reg_S):
    '''
    Check the channel is set as public
    '''
    user_id = user_reg_S

    channels_create_v1(user_id, 'SeamApple', True)
    channel = initial_object['channels'][0]
    assert channel['is_public'] == True


def test_channel_create_public_fail(clear, user_reg_S):
    '''
    Test if Inputerror is raise when the channel name is too long
    '''
    user_id = user_reg_S
    with pytest.raises(InputError):
        channels_create_v1(user_id, 'GroupofMonkeysDancingTogether', True)


def test_channel_create_private_success(clear, user_reg_S):
    '''
    Success case for create multiple channels with correct channel ID (Private)
    '''
    user_id = user_reg_S

    c_id = channels_create_v1(user_id, 'SeamBanana', False)
    assert c_id == {'channel_id': 0}
    c_id = channels_create_v1(user_id, 'SeamCoal', False)
    assert c_id == {'channel_id': 1}

def test_channel_create_private(clear, user_reg_S):
    '''
    Check the channel is set as private
    '''
    user_id = user_reg_S

    channels_create_v1(user_id, 'SeamBanana', False)
    channel = initial_object['channels'][0]
    assert channel['is_public'] == False

def test_channel_create_private_fail(clear, user_reg_S):
    '''
    Test if Inputerror is raised when the channel name is too short
    '''
    user_id = user_reg_S
    with pytest.raises(InputError):
        channels_create_v1(user_id, '', False)

def test_channel_create_invalid_auth_id(clear, user_reg_S):
    '''
    Test if Accesserror is rasied when a invalid user ID is provided
    '''
    with pytest.raises(AccessError):
        channels_create_v1(99999999, 'SeamApple', True)

def test_channel_create_no_user_id(clear):
    '''
    Test if Accesserror is rasied when no user ID is provided
    '''
    with pytest.raises(AccessError):
        channels_create_v1(88888888, 'SeamApple', True)
        
clear_v1()




