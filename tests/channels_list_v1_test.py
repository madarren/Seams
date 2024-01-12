'''
Tests for channels_list_v1.

'''
import pytest
from src.error import AccessError
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channels import channels_list_v1
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_reg_S():
    return auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')


def test_channels_list_invalid_user_id(clear):
    ''' Test that AccessError is raised for invalid token '''
    with pytest.raises(AccessError):
        channels_list_v1('abcdef')

def test_channels_list_public_channel(clear, user_reg_S):
    ''' Test that the list is showing the user id and channel name correctly '''
    channels_create_v1(user_reg_S['token'], 'Channel 1', True)
    assert channels_list_v1(user_reg_S['token']) == {'channels': [{'channel_id': 0, 'name': 'Channel 1'}]}   

def test_channels_list_not_joined(clear, user_reg_S):
    ''' Check if the user has not joined any channels '''
    assert channels_list_v1(user_reg_S['token']) == {'channels': []}

def test_channels_list_multiple_channels(clear, user_reg_S):
    ''' Test that the user is in multiple channels '''
    channel_1_dict = channels_create_v1(user_reg_S['token'], 'Channel 1', True)
    channel_1_id = channel_1_dict['channel_id']
    channel_2_dict = channels_create_v1(user_reg_S['token'], 'Channel 2', False)
    channel_2_id = channel_2_dict['channel_id']
    channel_1 = {'channel_id': channel_1_id, 'name': 'Channel 1'}
    channel_2 = {'channel_id': channel_2_id, 'name': 'Channel 2'}
    dict = []
    dict.append(channel_1)
    dict.append(channel_2)
    assert channels_list_v1(user_reg_S['token']) == {'channels': dict}

def test_list_two_channels(clear, user_reg_S):
    ''' Test when there are only two users and returns one users channel info '''
    id_dict = auth_register_v1('valid2@email.com', 'password', 'firstname', 'lastname')
    token = id_dict['token']
    channel_1_dict = channels_create_v1(user_reg_S['token'], 'Channel 1', True)
    channel_1_id = channel_1_dict['channel_id']
    channel_1 = {'channel_id': channel_1_id, 'name': 'Channel 1'}
    channels_create_v1(token, 'Channel 2', False)  
    dict = []
    dict.append(channel_1)
    assert channels_list_v1(user_reg_S['token']) == {'channels': dict}

clear_v1()
