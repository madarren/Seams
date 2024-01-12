'''
Tests for channel_details_v1
'''
import pytest
from src.error import InputError, AccessError
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_invite_v1, channel_details_v1
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_registration():
    return auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')

@pytest.fixture
def channel_registration(user_registration):
    channel_dict = channels_create_v1(user_registration['token'], "Channel 1", True)
    return channel_dict["channel_id"]


def test_invalid_auth_user(clear):
    ''' Test that an invalid token raises an AccessError. '''
    with pytest.raises(AccessError):
        channel_invite_v1("token", 3, 2)

def test_invalid_channel_id(clear, user_registration):
    ''' Test that a valid token but invalid channel id raises an InputError. '''
    with pytest.raises(InputError):
        channel_invite_v1(user_registration['token'], 3, 2)

def test_auth_user_not_member(clear, user_registration, channel_registration):
    ''' Test that a user owning the token not in the channel raises an AccessError. '''
    another_user_dict = auth_register_v1('anothervalid@email.com', 'password', 'anotherfirstname', 'anotherlastname')
    another_user_token = another_user_dict["token"]
    with pytest.raises(AccessError):
        channel_invite_v1(another_user_token, channel_registration, user_registration['auth_user_id'])

def test_invalid_u_id(clear, user_registration, channel_registration):
    ''' Test valid token and channel id but invalid user id raises InputError. '''
    with pytest.raises(InputError):
        channel_invite_v1(user_registration['token'], channel_registration, 2)

def test_u_id_already_member(clear, user_registration, channel_registration):
    ''' Test inviting an existing user raises InputError. '''
    with pytest.raises(InputError):
        channel_invite_v1(user_registration['token'], channel_registration, user_registration['auth_user_id'])

def test_valid_invite(clear, user_registration, channel_registration):
    ''' Test that invite works and adds another user to the channel. '''
    another_user_dict = auth_register_v1('anothervalid@email.com', 'password', 'anotherfirstname', 'anotherlastname')
    another_user_id = another_user_dict["auth_user_id"]
    channel_invite_v1(user_registration['token'], channel_registration, another_user_id)
    members = channel_details_v1(user_registration['token'], channel_registration)['all_members']
    assert another_user_id == members[1]['u_id']
    with pytest.raises(InputError):
        channel_invite_v1(user_registration['token'], channel_registration, another_user_id)

clear_v1()
