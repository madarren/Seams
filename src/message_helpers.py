"""
    This module contains functions that help with the logic of message.py.
    It contains a similar structure to that of token.py.
    There will be a global message tracker, a function that generates a message and appropriately adds it to store["messages"] 
    and a function that resets the message tracker for when clear is called. 
    There are also error checking functions specific to the message feature. 
"""

from src.data_store import data_store
from src.tokens import decode_token


global MESSAGE_TRACKER
MESSAGE_TRACKER = 0

def generate_new_message_id():
    """Generates a new sequential message ID

    Returns:
        number: The generated message ID
    """

    global MESSAGE_TRACKER
    message_id = MESSAGE_TRACKER
    MESSAGE_TRACKER += 1
    return message_id


def generate_message(token, channel_id, dm_id):
    """Creates a new message inside datastore. The actual message does not get saved inside store["messages"]. Instead it saves
    a dictionary containing keys message_id, auth_user_id and channel_id. The actual message will be saved inside store["channels"][channel_id]["messages"]

    Args: 
        token (string): token of user creating the message
        channel_id (int): channel_id of the channel the messasge is being sent to

    Returns:
        int: The message ID of the new message
    """

    store = data_store.get()

    auth_user_id = decode_token(token)["auth_user_id"]

    message_id = generate_new_message_id()
    store["messages"].append({"message_id": message_id, "auth_user_id": auth_user_id, "channel_id": channel_id, "dm_id": dm_id})
    data_store.set(store)

    return message_id

def reset_messages():
    """Resets the global messages, for when data store is reset.

    Returns:
        Empty dictionary.
    """
    global MESSAGE_TRACKER
    MESSAGE_TRACKER = 0
    return {}

def check_valid_message_id(token, message_id):    
    """ Checks whether the message id refers to a valid message inside a channel the user has joined

    Args:
        token (string): token for the user making the request
        message_id (int): allows the message to be uniquely identified

    Returns:
        boolean: True if the message id is valid 
    """

    store = data_store.get()

    auth_user_id = decode_token(token)["auth_user_id"]

    channel_id = -1
    dm_id = -1
    for message in store["messages"]:
        if message["message_id"] != message_id:
            continue
        else:
            channel_id = message["channel_id"]
            dm_id = message["dm_id"]


    if channel_id == -1 and dm_id == -1:
        return False
    
    if channel_id != -1 and auth_user_id in store["channels"][channel_id]["members"]:
        return True
    elif dm_id != -1:
        for member in store["dms"][dm_id]["members"]:
            if member["u_id"] != auth_user_id:
                continue
            else: 
                return True
    else: 
        return False


def check_valid_message_perms(token, message_id):
    """ Checks whether the user has permissions to access the message id 

    Args:
        token (string): token for the user making the request
        message_id (int): allows the message to be uniquely identified

    Returns:
        boolean: True if the user can access the message id
    """
    store = data_store.get()

    auth_user_id = decode_token(token)["auth_user_id"]

    channel_id = -1
    dm_id = -1
    for message in store["messages"]:
        if message["message_id"] == message_id:
            if message["auth_user_id"] == auth_user_id:
                return True
            else: 
                channel_id = message["channel_id"]
                dm_id = message["dm_id"]
    
    if channel_id != -1 and auth_user_id in store["channels"][channel_id]["owners"]:
        return True
    elif dm_id != -1 and auth_user_id == store["dms"][dm_id]["owners"]["u_id"]:
        return True
    else: 
        return False

def check_valid_owner_perms(token, message_id):
    """ Checks whether the user has permissions to access the message id 

    Args:
        token (string): token for the user making the request
        message_id (int): allows the message to be uniquely identified

    Returns:
        boolean: True if the user can access the message id
    """
    store = data_store.get()

    auth_user_id = decode_token(token)["auth_user_id"]

    channel_id = -1
    dm_id = -1
    for message in store["messages"]:
        if message["message_id"] != message_id:
            continue
        else: 
            channel_id = message["channel_id"]
            dm_id = message["dm_id"]
    
    if channel_id != -1 and auth_user_id in store["channels"][channel_id]["owners"]:
        return True
    elif dm_id != -1 and auth_user_id == store["dms"][dm_id]["owners"]["u_id"]:
        return True
    else: 
        return False


def load_message_tracker(message_tracker):
    global MESSAGE_TRACKER
    MESSAGE_TRACKER = message_tracker


def check_react_id(token, message_id):    
    """ Checks whether the the message already contains a react id from the auth_user 

    Args:
        token (string): token for the user making the request
        message_id (int): allows the message to be uniquely identified
        react_id (int): the id of the type of react

    Returns:
        boolean: True if the message does not yet have a react from the user 
    """

    store = data_store.get()

    auth_user_id = decode_token(token)["auth_user_id"]

    channel_id = -1
    dm_id = -1
    for message in store["messages"]:
        if message["message_id"] != message_id:
            continue
        else:
            channel_id = message["channel_id"]
            dm_id = message["dm_id"]


    if channel_id != -1:
        for ch_message in store["channels"][channel_id]["message"]:
            if ch_message["message_id"] == message_id:
                if auth_user_id in ch_message["reacts"][0]["u_ids"]:
                    return True 
    else:
        for dm_message in store["dms"][dm_id]["message"]:
            if dm_message["message_id"] == message_id:
                if auth_user_id in dm_message["reacts"][0]["u_ids"]:
                    return True 

    return False

def check_pin(message_id):    
    """ Checks whether the the message is pinned or not

    Args:
        token (string): token for the user making the request
        message_id (int): allows the message to be uniquely identified
        react_id (int): the id of the type of react

    Returns:
        boolean: True if the message does not yet have a react from the user 
    """

    store = data_store.get()

    channel_id = -1
    dm_id = -1
    for message in store["messages"]:
        if message["message_id"] != message_id:
            continue
        else:
            channel_id = message["channel_id"]
            dm_id = message["dm_id"]


    if channel_id != -1:
        for ch_message in store["channels"][channel_id]["message"]:
            if ch_message["message_id"] == message_id:
                return ch_message["is_pinned"]
    else:
        for dm_message in store["dms"][dm_id]["message"]:
            if dm_message["message_id"] == message_id:
                return dm_message["is_pinned"]
