'''
Test file for channel_join_v1
'''

import pytest 

from src.data_store import initial_object
from src.auth import auth_register_v1, auth_login_v1 
from src.channels import channels_create_v1
from src.channel import channel_join_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.tokens import *


@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_reg_S():
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    data = auth_login_v1('valid@email.com', 'password')
    return data['token']

@pytest.fixture
def user_reg_S2():
    auth_register_v1('xyz@world.io', 'helloWorld', 'Python', 'Snake')
    data = auth_login_v1('xyz@world.io', 'helloWorld')
    return data['token']

def test_channel_join_private(clear, user_reg_S, user_reg_S2):
    '''
    Test if Accesserror is raised when a normal user tried to join a private channel
    '''
    c_owner = user_reg_S
    c_dict = channels_create_v1(c_owner, 'SeamEgg', False)
    c_id = c_dict["channel_id"]
    u_token = user_reg_S2
    with pytest.raises(AccessError):
        channel_join_v1(u_token, c_id)
    
def test_channel_join_invalid_token(clear):
    '''
    Test if Accesserror is raised when token is invalid
    '''
    with pytest.raises(AccessError):
        channel_join_v1(88888888, 88888888)

def test_channel_join_channel_id_not_found(clear, user_reg_S):
    '''
    Test if Inputerror is raised when channel ID no exist / invalid
    '''
    u_token = user_reg_S
    with pytest.raises(InputError):
        channel_join_v1(u_token, 88888888)

def test_channel_join_is_member_already(clear, user_reg_S, user_reg_S2):
    '''
    Test if Inputerror is raised when user tried to join but already a member of the channel
    '''
    c_owner = user_reg_S
    c_dict = channels_create_v1(c_owner, 'SeamEgg', True)
    c_id = c_dict['channel_id']
    u_token = user_reg_S2
    channel_join_v1(u_token, c_id)
    with pytest.raises(InputError):
        channel_join_v1(u_token, c_id)

def test_channel_join_public_Seamfounder(clear, user_reg_S, user_reg_S2):
    '''
    Test if global owner able to join the channel (Public)
    '''
    S_owner = user_reg_S
    u_token = user_reg_S2
    c_dict = channels_create_v1(u_token, 'SeamEgg', True)
    c_id = c_dict['channel_id']
    channel_join_v1(S_owner, c_id)
    payload = decode_token(user_reg_S)
    S_owner = payload['auth_user_id']
    c_member = initial_object['channels'][c_id]['members'][1]
    assert c_member == S_owner

def test_channel_join_private_not_Seamfounder(clear, user_reg_S, user_reg_S2):
    '''
    Test if Accesserror is raised when user not a global owner when joining private channel
    '''
    S_owner = user_reg_S
    u_token = user_reg_S2
    c_dict = channels_create_v1(S_owner, 'SeamEgg', False)
    c_id = c_dict['channel_id']
    with pytest.raises(AccessError):
        channel_join_v1(u_token, c_id)

def test_channel_join_private_Seamfounder(clear, user_reg_S, user_reg_S2):
    '''
    Test if global owner able to join the channel (Private)
    '''
    S_owner = user_reg_S
    u_token = user_reg_S2
    c_dict = channels_create_v1(u_token, 'SeamEgg', False)
    c_id = c_dict['channel_id']
    channel_join_v1(S_owner, c_id)
    payload = decode_token(user_reg_S)
    S_owner = payload['auth_user_id']
    c_member = initial_object['channels'][c_id]['members'][1]
    assert c_member == S_owner


clear_v1()

