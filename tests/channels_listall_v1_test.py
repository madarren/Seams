'''
Tests for channels_listall_v1.
'''
import pytest
from src.error import AccessError
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channels import channels_listall_v1
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_reg():
    return auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')['token']


def test_listall_invalid_input(clear):
    ''' Test AccessError is raised when invalid token is given. '''
    with pytest.raises(AccessError):
        assert channels_listall_v1('token')

def test_listall_no_channels(clear, user_reg): 
    ''' Test function works even with no channels. '''  
    assert channels_listall_v1(user_reg) == {'channels': []}

def test_listall_one_channel(clear, user_reg):
    ''' Test the function works with one channel. '''
    c_id = channels_create_v1(user_reg, 'Channel 1', True)['channel_id']
    assert channels_listall_v1(user_reg) == {'channels': [{'channel_id': c_id, 'name': 'Channel 1'}]}

def test_listall_two_channels(clear, user_reg):
    ''' Test function works with private and public channels, with different members. '''
    token2 = auth_register_v1('valid2@email.com', 'password', 'firstname', 'lastname')['token']
    channel_1_dict = channels_create_v1(user_reg, 'Channel 1', True)
    c1_id = channel_1_dict['channel_id']
    channel_2_dict = channels_create_v1(token2, 'Channel 2', False)  
    c2_id = channel_2_dict['channel_id']
    channel_1 = {'channel_id': c1_id, 'name': 'Channel 1'}
    channel_2 = {'channel_id': c2_id, 'name': 'Channel 2'}
    dict = []
    dict.append(channel_1)
    dict.append(channel_2)
    assert channels_listall_v1(user_reg) == {'channels': dict}
    assert channels_listall_v1(token2) == {'channels': dict}

clear_v1()
