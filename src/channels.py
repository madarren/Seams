''' 
channels.py

This file contains the channels functions. These include the list, listall, and create
functions which create the channels and list the channels that a user is part of.

'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token, stat_user_channel_add
from src.tokens import *
from src.persistence import save_data
import datetime

def channels_list_v1(token):
    """
    Provides a list of all channels (and their associated details) that a user is part of.

    Exceptions:
        AccessError: token invalid

    Args:
        string: token

    Returns:
        Dictionary containing lists which contains dictionaries of {channel_id, name}
    """
    store = data_store.get()
    # Check if user have valid user
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")

    # list the channels the user is part of with channel id and channel name
    channels = []
    payload = decode_token(token)
    auth_user_id = payload['auth_user_id']
    for channel in store["channels"]:
        for member in channel["members"]:
            if auth_user_id == member:
                channels.append({'channel_id': channel['channel_id'], 'name': channel['name']})            
                break
    return {'channels': channels}

def channels_listall_v1(token):
    """ 
    Provides a list of all channels including private channels (and their associated details).

    Exceptions:
        AccessError: token invalid

    Args: 
        string: token

    Returns: 
        Dictionary containing types { channels, channel_name}
    """
    # Check if user have valid user
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")
    
    store = data_store.get()
    channels = []
    for channel in store["channels"]:
        channels.append({'channel_id': channel['channel_id'], 'name': channel['name']})
    return {'channels': channels}

def channels_create_v1(token, name, is_public):
    '''
    Given token, name and option for whether the channel is public or priavte (True / False), 
    create a new channel with their preference and add them into the channel

    Exceptions:
        AccessError: When token is invalid
        InputError: When the length of channel name is less than 1 or more than 20 characters

    Args:
        string: token
        string: name
        string: is_public

    Return:
        Dictionary: {'channel_id': int }
    '''
    store = data_store.get()

    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")
    
    if len(name) < 1 or len(name) > 20:
        raise InputError(description="Invalid Name")

    channel_id = len(store['channels'])
    auth_user_id = decode_token(token)['auth_user_id']

    new_channel = {
        'name': name,
        'is_public': is_public,
        'channel_id': channel_id,
        'owners': [auth_user_id],
        'members': [auth_user_id],
        'message': [],
        'standup': {
            'msgqueue': [],
            'is_active': False,
            'time_finish': None
        }
    }

    dt = int(datetime.datetime.now().timestamp())
    store['channels'].append(new_channel)
    stat_user_channel_add(auth_user_id, dt)
    num_channels = store['workspace']['channels'][-1]['num_channels_exist']
    store['workspace']['channels'].append({'num_channels_exist': num_channels + 1, 'time_stamp': dt})
    data_store.set(store)
    save_data()
    return {'channel_id': channel_id}
