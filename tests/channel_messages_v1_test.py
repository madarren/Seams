'''
Tests for channel_messaegs_v1
'''
import pytest

from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_messages_v1
from src.data_store import initial_object
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_reg_S():
    id_dict = auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    return id_dict['token']


def test_invalid_user(clear):
    ''' invalid token (and channel but AccessError has higher priority)'''
    with pytest.raises(AccessError):
        channel_messages_v1("invalidtoken", 3, 0)

def test_invalid_channel(clear, user_reg_S):
    ''' invalid channel_id (valid token now)'''
    with pytest.raises(InputError):
        channel_messages_v1(user_reg_S, 3, 0)

def test_start_number_too_big(clear, user_reg_S):
    ''' currently have 0 messages right now, so 10 > 0'''
    channel_dict = channels_create_v1(user_reg_S, "Channel 1", True)
    channel_id = channel_dict["channel_id"]
    with pytest.raises(InputError):
        channel_messages_v1(user_reg_S, channel_id, 10)

def test_valid_but_no_messages(clear, user_reg_S):
    ''' test valid but no messages'''
    channel_dict = channels_create_v1(user_reg_S, "Channel 1", True)
    channel_id = channel_dict["channel_id"]
    assert channel_messages_v1(user_reg_S, channel_id, 0) == {"messages": [], "start": 0, "end": -1}

def test_auth_user_non_member(clear, user_reg_S):
    ''' test token used to call route is not actually in the channel'''
    channel_dict = channels_create_v1(user_reg_S, "Channel 1", True)
    channel_id = channel_dict["channel_id"]

    id_dict = auth_register_v1("anothervalid@email.com", "password", "anotherfirstname", "anotherlastname")
    another_user_token = id_dict["token"]

    with pytest.raises(AccessError):
        channel_messages_v1(another_user_token, channel_id, 0)

clear_v1()
