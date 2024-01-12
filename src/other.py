'''
other.py

This file contains the clear function. This function clears the data store.
This file also has two recurring checks that have been made into functions.
These are for the AccessError of auth_user_id and tokens.
There are also additional helper functions that are included in this file.

'''
from src.data_store import data_store
from src.tokens import reset_sessions, decode_token
from src.message_helpers import reset_messages
import hashlib
from src.persistence import save_data

def clear_v1():
    """Resets the data store to its empty state. Resets session and message tracker.
    
    No arguments or exceptions.

    Returns:
        Empty dictionary.
    """
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['tokens'] = []
    store['messages'] = []
    store['dms'] = []
    store['workspace'] = {
        'channels': [],
        'dms': [],
        'messages': [],
        'num_users': 0,
    }
    data_store.set(store)
    reset_sessions()
    reset_messages()
    save_data()
    return {}


def hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_auth_user_id(auth_user_id):
    ''' Checks if the auth_user_id exists. If exists return True, else False.

    Args:
        integer: auth_user_id

    Returns:
        boolean
    '''
    store = data_store.get()
    for user in store['users']:
        if user["id"] != auth_user_id:
            continue
        else:
            return True
    return False

def check_valid_token(token):
    ''' Checks if the token exists. If exists return True, else False.

    Args:
        string: token

    Returns:
        boolean
    '''
    store = data_store.get()
    for stored_token in store['tokens']:
        if stored_token != token:
            continue
        else:
            return True
    return False

def check_valid_channel_id(channel_id):
    ''' Checks if the channel_id exists. If exists return True, else False.

    Args:
        int: channel_id

    Returns:
        boolean
    '''
    store = data_store.get()
    for channel in store["channels"]:
        if channel["channel_id"] != channel_id:
            continue
        else:
            return True
    return False


def check_channel_memebers(channel_id, u_ID):
    '''
    Check if the user is in the channel member list

    Args:
        int: channel_id
        int: u_ID

    Returns:
        boolean
    '''
    store = data_store.get()
    members = store["channels"][channel_id]["members"]
    for member in members:
        if u_ID != member:
            continue
        else:
            return True
    return False

def check_channel_owners(channel_id, u_ID):
    '''
    Check if the user is in the channel owner list

    Args:
        int: channel_id
        int: u_ID

    Returns:
        boolean
    '''
    store = data_store.get()
    owners = store["channels"][channel_id]["owners"]
    for owner in owners:
        if u_ID != owner:
            continue
        else:
            return True
    return False

def get_permission(u_id):
    ''' Given a valid user id, return that user's global permissions. 

    Args:
        int: u_id

    Returns:
        int: 1 if global owner, 2 if global user.
    '''
    store = data_store.get()
    return store['users'][u_id - 1]['global_permission']

def check_valid_dm_id(dm_id):
    ''' Checks if the dm_id exists. If exists return True, else False.

    Args:
        int: dm_id

    Returns:
        boolean
    '''
    store = data_store.get()
    for dms in store["dms"]:
        if dms["dm_id"] != dm_id:
            continue
        else:
            return True
    return False

def check_user_in_dm(token, dm_id):
    payload = decode_token(token)
    auth_user_id = payload['auth_user_id']

    store = data_store.get()
    dms = store['dms'][dm_id]
    for users in dms["members"]:
        if users["u_id"] != auth_user_id:
            continue
        else:
            return True
    return False

def stat_user_channel_add(auth_user_id, dt):
    ''' Update a user's stats when they join a channel. '''
    store = data_store.get()
    num_ch = store['users'][auth_user_id - 1]['stats']['channels'][-1]['num_channels_joined']
    store['users'][auth_user_id - 1]['stats']['channels'].append({
        'num_channels_joined': num_ch + 1,
        'time_stamp': dt,
    })
    data_store.set(store)
    return {}

def stat_user_channel_remove(auth_user_id, dt):
    ''' Update a user's stats when they leave a channel. '''
    store = data_store.get()
    num_ch = store['users'][auth_user_id - 1]['stats']['channels'][-1]['num_channels_joined']
    store['users'][auth_user_id - 1]['stats']['channels'].append({
        'num_channels_joined': num_ch - 1,
        'time_stamp': dt,
    })
    data_store.set(store)
    return {}

def stat_user_dm_add(auth_user_id, dt):
    ''' Update a user's stats when they join a dm. '''
    store = data_store.get()
    num_dm = store['users'][auth_user_id - 1]['stats']['dms'][-1]['num_dms_joined']
    store['users'][auth_user_id - 1]['stats']['dms'].append({
        'num_dms_joined': num_dm + 1,
        'time_stamp': dt,
    })
    data_store.set(store)
    return {}

def stat_user_dm_remove(auth_user_id, dt):
    ''' Update a user's stats when they leave a dm'''
    store = data_store.get()
    num_dm = store['users'][auth_user_id - 1]['stats']['dms'][-1]['num_dms_joined']
    store['users'][auth_user_id - 1]['stats']['dms'].append({
        'num_dms_joined': num_dm - 1,
        'time_stamp': dt,
    })
    data_store.set(store)
    return {}


def stat_user_message_add(auth_user_id, dt):
    ''' Update a user's stats when they send a message'''
    store = data_store.get()
    num_msg = store['users'][auth_user_id - 1]['stats']['messages'][-1]['num_messages_sent']
    store['users'][auth_user_id - 1]['stats']['messages'].append({
        'num_messages_sent': num_msg + 1,
        'time_stamp': dt,
    })
    data_store.set(store)
    return {}