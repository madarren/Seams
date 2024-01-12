'''
standup.py

This contains functions for standup. These include standup_start, standup_active 
and standup_send
'''
from datetime import datetime, timedelta
from threading import Timer
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import *
from src.tokens import *
from src.message import message_send_v1
from src.persistence import save_data

def standup_start_v1(token, channel_id, length):
    '''
    Given token, channel ID and length, start standup in the channel

    Exceptions:
        AccessError: 
            When token is not valid
            When user is not a member of the channel

        InputError: 
            Channel ID is not valid
            Length is invalid (< 0)
            When another standup is active

    Args:
        string: token
        int: channel_id
        int: length

    Return:
        Dictionary: {'time_finish': }
    '''
    
    store = data_store.get()

    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")

    if check_valid_channel_id(channel_id) != True:
        raise InputError(description="Channel ID does not exist")

    payload = decode_token(token)
    auth_user_id = payload['auth_user_id']
    if check_channel_memebers(channel_id, auth_user_id) != True:
        raise AccessError(description="You are not in the channel")

    if length < 0:
        raise InputError(description="length cannot be negative")

    standup = store['channels'][channel_id]['standup'] 
    if standup['is_active']:
        raise InputError(description="An active standup is running")

    standup['is_active'] = True
    # standup['user'] = auth_user_id
    finish_time = (datetime.now() + timedelta(seconds=length)).timestamp()
    standup['time_finish'] = finish_time
    
    data_store.set(store)
    save_data()

    Timer(length, standup_msg_queue, [token, channel_id]).start()

    return {'time_finish': finish_time}

def standup_active_v1(token, channel_id):
    '''
    Given token and channel ID, check if there is any standup is active

    Exceptions:
        AccessError: 
            When token is not valid
            When user is not a member of the channel

        InputError: 
            Channel ID is not valid


    Args:
        string: token
        int: channel_id

    Return:
        Dictionary: {'is_active': ,'time_finish': }
    '''
    store = data_store.get()

    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")

    if check_valid_channel_id(channel_id) != True:
        raise InputError(description="Channel ID does not exist")

    payload = decode_token(token)
    auth_user_id = payload['auth_user_id']
    if check_channel_memebers(channel_id, auth_user_id) != True:
        raise AccessError(description="You are not in the channel")

    standup = store['channels'][channel_id]['standup'] 
    if standup['is_active']:
        return {
            'is_active': True,
            'time_finish': standup['time_finish'],
        }

    return {
        'is_active': False,
        'time_finish': None,
    }

def standup_send_v1(token, channel_id, message):
    '''
    Given token, channel ID and message, store message that send during standup in queue

    Exceptions:
        AccessError: 
            When token is not valid
            When user is not a member of the channel

        InputError: 
            Channel ID is not valid
            When message is too long (> 1000)
            Standup is not acitve in the channel

    Args:
        string: token
        int: channel_id
        string: message

    Return:
        Dictionary: {'is_active': ,'time_finish': }
    '''
    store = data_store.get()

    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")

    if check_valid_channel_id(channel_id) != True:
        raise InputError(description="Channel ID does not exist")

    payload = decode_token(token)
    auth_user_id = payload['auth_user_id']
    if check_channel_memebers(channel_id, auth_user_id) != True:
        raise AccessError(description="You are not in the channel")

    if len(message) > 1000:
        raise InputError(description="Message too long")

    standup = store['channels'][channel_id]['standup']
    if standup['is_active'] == False or standup == None:
        raise InputError(description="Standup is not active")

    handle = store["users"][auth_user_id - 1]["handle"]
    messages = {
        'handle': handle,
        'message': message,
    }
    queue = standup['msgqueue']
    queue.append(messages)

    data_store.set(store)
    save_data()

    return {}

def standup_msg_queue(token, channel_id):
    '''
    Supplement function for standup_start_v1

    Given token and channel ID, send out messages that are send from standup_send_v1
    after standup is finished

    Exceptions:
        *Assume token and channel_id is checked in standup_start_v1

    Args:
        string: token
        int: channel_id

    Return:
        None (See message_send_v1)
    '''
    store = data_store.get()

    standup = store['channels'][channel_id]['standup']
    standup['is_active'] = False
    standups = ""
    for messages in standup["msgqueue"]:
        standups += messages['handle'] + ": " + messages['message'] + "\n"
    standups.rstrip()

    message_send_v1(token, channel_id, standups)