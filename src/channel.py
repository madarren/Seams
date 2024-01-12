'''
channel.py

This contains the channel functions. These include the invite, details, messages and join functions
for which a user can add another user into a channel, get the details of a channel they're in,
get the messages of a channel, or join another channel. For user have owner permission, they can
add/remove a user to owner list.

'''
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import *
from src.tokens import *
from src.message_helpers import check_react_id
from src.persistence import save_data
import datetime


def channel_invite_v1(token, channel_id, u_id):
    ''' An existing member of the channel invites another existing member to the channel. 
        The user automatically joins the channel once invited.

        Exceptions: 
            Access error if the token is invalid.
            Acess error when member inviting is not a member of the channel.
            Input error if the channel_id or u_id is incorrect.
            Input error if user is already a member of the channel. 

        Args: 
            string: token
            integer: channel_id
            integer: u_id

        Returns:
            empty dictionary.
    '''
    store = data_store.get()

    # Check token is a registered user
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Check channel_id is an existing channel.
    if not check_valid_channel_id(channel_id):
        raise InputError(description="Invalid channel id")

    auth_u_id = decode_token(token)["auth_user_id"]
    # Check auth user is in the channel 
    if not check_channel_memebers(channel_id, auth_u_id):
        raise AccessError(description="Auth user not in channel")

    # Check u_id is registered
    if not check_auth_user_id(u_id):
        raise InputError(description="User ID provided not registered")

    # Check user is not in the channel. Only check members becasue all owners are members
    if check_channel_memebers(channel_id, u_id):
        raise InputError(description="User is already a member")

    # Add user to channel
    store["channels"][channel_id]["members"].append(u_id)
    dt = int(datetime.datetime.now().timestamp())
    stat_user_channel_add(u_id, dt)
    data_store.set(store)
    save_data()
    return {}

def channel_details_v1(token, channel_id):
    """Given a channel with ID channel_id that the authorised user is a member of, 
    provide basic details about the channel.

    Exceptions:
        AccessError if the token does not exist.
        InputError if the channel does not exist.
        AccessError if the token's auth user id is not in the channel.

    Args:
        string: token
        intger: channel_id

    Returns:
        dictionary containing:
            'name': string (this is the name of the channel)
            'is_public': boolean
            'owner_members': list of dictionaries
            'all_members': list of dictionaries
    """
    store = data_store.get()

    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Check the channel exists.
    if not check_valid_channel_id(channel_id):
        raise InputError(description="Invalid channel id")

    u_id = decode_token(token)["auth_user_id"]
    # Check if user is part of the channel.
    if not check_channel_memebers(channel_id, u_id):
        raise AccessError(description="User not in channel")

    # Get the channel details.
    channel = store['channels'][channel_id]
    name, public = channel['name'], channel['is_public']
    owners, members = [], []
    for owner in channel['owners']:
        owner_info = store["users"][owner - 1]
        owner_details = {
            'u_id': owner,
            'email': owner_info['email'],
            'name_first': owner_info['first_name'],
            'name_last': owner_info['last_name'],
            'handle_str': owner_info['handle'],
            'profile_img_url': owner_info['profile_img_url'],
        }
        owners.append(owner_details)
    
    for member in channel['members']:
        member_info = store["users"][member - 1]
        member_details = {
            'u_id': member,
            'email': member_info['email'],
            'name_first': member_info['first_name'],
            'name_last': member_info['last_name'],
            'handle_str': member_info['handle'],
            'profile_img_url': member_info['profile_img_url'],
        }
        members.append(member_details)

    return {
        'name': name,
        'is_public': public,
        'owner_members': owners,
        'all_members': members,
    }

def channel_messages_v1(token, channel_id, start):
    """ Given all valid channel_id and tokens, the function will return up to 50 messages between the index "start" and "start + 50", as well
    as the start and end indices. 

    Args:
        token (string): token is used to identify the user calling the function
        channel_id (int): channel_id refers to the channel that the messages are returned from
        start (int): the starting index of the returned messages

    Raises:
        AccessError: invalid token (does not exist in datastore)
        InputError: invalid channel_id (does not exist in datastore)
        AccessError: channel_id and token are valid but the token does not refer to a member of the channel
        InputError: the start index is greater than the total number of messages in the channel 

    Returns:
        dictionary containing: 
            "messages": a list of up to 50 messages between the "start" index and "start + 50"
            "start": the starting index, the same as the paramater
            "end": the index of the last message, either "start + 50" if there are enough messages or "-1" if there are not enough
    """
    store = data_store.get()

    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_channel_id(channel_id):
        raise InputError(description="Invalid channel id")

    u_id = decode_token(token)["auth_user_id"]
    if not check_channel_memebers(channel_id, u_id):
        raise AccessError(description="User not in channel")

    # start is greater than the total number of messages in the channel
    total_messages = len(store["channels"][channel_id]["message"])
    if start >= total_messages and (total_messages != 0 or start != 0):
        raise InputError(description="Not enough messages")

    end = min(start + 50, total_messages)
    if start + 50 >= total_messages: 
        temp_end = -1
    else: 
        temp_end = end

    i = start
    message_history = [] 
    while i < end:
        if check_react_id(token, store["channels"][channel_id]["message"][total_messages - 1 - i]["message_id"]):
            store["channels"][channel_id]["message"][total_messages - 1 - i]["reacts"][0]["is_this_user_reacted"] = True
        else: 
            store["channels"][channel_id]["message"][total_messages - 1 - i]["reacts"][0]["is_this_user_reacted"] = False
        message_history.append(store["channels"][channel_id]["message"][total_messages - 1 - i])
        i += 1

    return {
        "messages": message_history,
        "start": start,
        "end": temp_end,
    }

def channel_join_v1(token, channel_id):
    '''
    Given token and channel ID, add a user the the channel

    Exceptions:
        AccessError: 
            When token is not valid
            When channel is set to private. 
            Not a global owner
        InputError: 
            Channel ID is not valid.
            User is already a member of the channel.

    Args:
        string: token
        int: channel_id

    Return:
        Dictionary: {}
    '''
    store = data_store.get()

    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")
    
    if check_valid_channel_id(channel_id) != True:
        raise InputError(description="Channel ID does not exist")

    payload = decode_token(token)
    auth_user_id = payload['auth_user_id']
    if check_channel_memebers(channel_id, auth_user_id):
        raise InputError(description="User is already a member in channel")

    user = store['users'][auth_user_id - 1]
    chan = store["channels"][channel_id]
    if chan["is_public"] == False and user["global_permission"] == 2:
        raise AccessError(description="You don't have permission")   

    store['channels'][channel_id]['members'].append(auth_user_id)
    dt = int(datetime.datetime.now().timestamp())
    stat_user_channel_add(auth_user_id, dt)
    data_store.set(store)
    save_data()
    return {}

def channel_leave_v1(token, channel_id):
    '''
    Given token and channel ID, remove a user the the channel

    Exceptions:
        AccessError: 
            When token is not valid
            When user is not a member of the channel
        InputError: 
            Channel ID is not valid.

    Args:
        string: token
        int: channel_id

    Return:
        Dictionary: {}
    '''
    store = data_store.get()

    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")

    if check_valid_channel_id(channel_id) != True:
        raise InputError(description="Channel ID does not exist")

    auth_user_id = decode_token(token)['auth_user_id']

    if auth_user_id in store["channels"][channel_id]["members"]:
        store["channels"][channel_id]["members"].remove(auth_user_id)
    else:
        raise AccessError(description="You are not in the channel")

    if auth_user_id in store["channels"][channel_id]["owners"]:
        store["channels"][channel_id]["owners"].remove(auth_user_id)

    dt = int(datetime.datetime.now().timestamp())
    stat_user_channel_remove(auth_user_id, dt)
    data_store.set(store)
    save_data()
    return {}

def channel_addowner_v1(token, channel_id, u_id):
    '''
    Given token, channel ID and u_id, add a user (u_id) to the channel owner list

    Exceptions:
        AccessError: 
            When token is not valid
            When user (token) does not have owner permissions

        InputError: 
            Channel ID is not valid.
            When u_id is not valid
            When u_id is not found in the channel (not a member)
            When u_id is already an owner

    Args:
        string: token
        int: channel_id
        int: u_id

    Return:
        Dictionary: {} 
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


    if check_auth_user_id(u_id) != True:
        raise InputError(description="User not found")

    if check_channel_memebers(channel_id, u_id) != True:
        raise InputError(description="User is not in the channel")


    if check_channel_owners(channel_id, u_id) == True:
        raise InputError(description="User is already an owner of the channel")


    user = store['users'][auth_user_id - 1]
    if check_channel_owners(channel_id, auth_user_id) != True:
        if user["global_permission"] == 2: 
            raise AccessError(description="You don't have permission")

    owners = store['channels'][channel_id]['owners'] 
    owners.append(u_id)
    data_store.set(store)
    save_data()
    return {}
    
def channel_removeowner_v1(token, channel_id, u_id):
    '''
    Given token, channel ID and u_id, remove a user (u_id) from the channel owner list

    Exceptions:
        AccessError: 
            When token is not valid
            When user (token) does not have owner permissions

        InputError: 
            Channel ID is not valid
            When u_id is not valid
            When u_id is not found in owner list (not an owner)
            When u_id is the only owner in the channel

    Args:
        string: token
        int: channel_id
        int: u_id

    Return:
        Dictionary: {}
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

    if check_auth_user_id(u_id) != True:
        raise InputError(description="User not found")

    if check_channel_owners(channel_id, u_id) != True:
        raise InputError(description="User is not an owner of the channel")

    user = store['users'][auth_user_id - 1]
    if check_channel_owners(channel_id, auth_user_id) != True:
        if user["global_permission"] == 2: 
            raise AccessError(description="You don't have permission")

    owners = store['channels'][channel_id]['owners']
    if len(owners) == 1:
        raise InputError(description="User is the only owner in the channel")

    owners = store['channels'][channel_id]['owners']
    for owner in owners:
        if u_id == owner:
            owners.remove(owner)
    data_store.set(store)
    save_data()
    return {}
