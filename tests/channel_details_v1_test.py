'''
Tests for channel_details_v1
'''
import pytest
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_join_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_reg_S():
    return auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')


def test_no_valid_ids(clear):
    ''' Test that an invalid token and channel id raises an AccessError. '''
    with pytest.raises(AccessError):
        channel_details_v1('token', 100)

def test_valid_token_invalid_channel(clear, user_reg_S):
    ''' Test that a valid token but invalid channel id raises an InputError. ''' 
    with pytest.raises(InputError):
        channel_details_v1(user_reg_S['token'], 100)
    
def test_invalid_token_valid_channel(clear, user_reg_S):
    ''' Test that an invalid token but valid channel raises an AccessError. '''
    chan_dict = channels_create_v1(user_reg_S['token'], "apple", True)
    chan_id = chan_dict['channel_id']
    with pytest.raises(AccessError):
        channel_details_v1("token", chan_id)

def test_token_not_in_channel(clear, user_reg_S):
    ''' Test that a valid token not in the valid channel raises an AccessError. '''
    chan_dict = channels_create_v1(user_reg_S['token'], "apple", True)
    chan_id = chan_dict['channel_id']
    id_dict = auth_register_v1("second@email.com", "password", "first", "last")
    another_user_token = id_dict["token"]
    with pytest.raises(AccessError):
        channel_details_v1(another_user_token, chan_id)

def test_correct_name(clear, user_reg_S):
    ''' Test that the correct channel names will be returned from different channels. '''
    chan1_dict = channels_create_v1(user_reg_S['token'], "apple", True)
    chan1_id = chan1_dict['channel_id']
    chan1_details = channel_details_v1(user_reg_S['token'], chan1_id)
    assert chan1_details['name'] == "apple"

    chan2_dict = channels_create_v1(user_reg_S['token'], "window", True)
    chan2_id = chan2_dict['channel_id']
    chan2_details = channel_details_v1(user_reg_S['token'], chan2_id)
    assert chan2_details['name'] == "window"

def test_correct_public_private(clear, user_reg_S):
    ''' Test the correct public status is returned from different channels. '''
    chan1_dict = channels_create_v1(user_reg_S['token'], "apple", True)
    chan1_id = chan1_dict['channel_id']
    chan1_details = channel_details_v1(user_reg_S['token'], chan1_id)
    assert chan1_details['is_public'] == True

    chan2_dict = channels_create_v1(user_reg_S['token'], "window", False)
    chan2_id = chan2_dict['channel_id']
    chan2_details = channel_details_v1(user_reg_S['token'], chan2_id)
    assert chan2_details['is_public'] == False

def test_correct_owner_members(clear, user_reg_S):
    ''' Test the owner of a channel is returned. '''
    chan1_dict = channels_create_v1(user_reg_S['token'], "apple", True)
    chan1_id = chan1_dict['channel_id']
    chan1_details = channel_details_v1(user_reg_S['token'], chan1_id)
    chan1_owners = chan1_details['owner_members']
    correct_owner = [
        {
            'u_id': user_reg_S['auth_user_id'],
            'email': "valid@email.com",
            'name_first': "firstname",
            'name_last': "lastname",
            'handle_str': "firstnamelastname",
            'profile_img_url': 'static/default.jpg',
        }
    ]
    assert chan1_owners == correct_owner

def test_correct_all_members(clear, user_reg_S):
    ''' Test the members of a channel are returned. ''' 
    id_dict = auth_register_v1('second@email.com', 'password', 'dio', 'brando')
    chan_dict = channels_create_v1(user_reg_S['token'], "apple", True)
    chan_id = chan_dict['channel_id']
    channel_join_v1(id_dict['token'], chan_id)
    chan_members = channel_details_v1(user_reg_S['token'], chan_id)['all_members']
    correct_members = [
        {
            'u_id': user_reg_S['auth_user_id'],
            'email': "valid@email.com",
            'name_first': "firstname",
            'name_last': "lastname",
            'handle_str': "firstnamelastname",
            'profile_img_url': 'static/default.jpg',
        },
        {
            'u_id': id_dict['auth_user_id'],
            'email': "second@email.com",
            'name_first': "dio",
            'name_last': "brando",
            'handle_str': "diobrando",
            'profile_img_url': 'static/default.jpg',
        }
    ]
    assert chan_members == correct_members
    assert channel_details_v1(id_dict['token'], chan_id)['all_members'] == correct_members
    clear_v1()
