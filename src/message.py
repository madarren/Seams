'''
message.py

This contains the message functions. These include the send, edit and remove functions
for which we can send new messages, update and remove pre-existing.

'''
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import check_valid_token, check_valid_channel_id, check_channel_memebers, check_valid_dm_id, check_user_in_dm, get_permission, stat_user_message_add
from src.message_helpers import generate_message, check_valid_message_id, check_valid_message_perms, check_react_id, check_valid_owner_perms, check_pin
from src.persistence import save_data
from src.tokens import decode_token
from threading import Timer

import datetime, time 

def message_send_v1(token, channel_id, message):
    """ Given a valid token and channel_id, a message will be sent to the channel_id from the token (auth user). The message and message_id will be 
        saved inside the channels messages database and the auth_user_id, message_id and channel_id will be saved inside the datastore. The function returns 
        the messages id.

    Args:
        token (string): auth users token that sent the message
        channel_id (int): the channel id that the message will be sent to
        message (string): the message that will be sent and stored inside the channel

    Raises:
        AccessError: invalid token (does not exist in datastore)
        InputError: invalid channel_id (does not exist in datastore)
        AccessError: channel_id and token are valid but the token does not refer to a member of the channel
        InputError: the message length either exceeds 1000 characters, or is an empty message (0 characters)

    Returns:
        dictionary containig: 
            "message_id": the id of the message that was sent  
    """
    store = data_store.get()
    

    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_channel_id(channel_id):
        raise InputError(description="Invalid channel id")

    u_id = decode_token(token)["auth_user_id"]
    if not check_channel_memebers(channel_id, u_id):
        raise AccessError(description="User not in channel")

    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Message length too long or too short")

    message_id = generate_message(token, channel_id, -1)

    new_message = {"message_id": message_id, "u_id": u_id, "message": message, "time_sent": int( time.time()), "reacts": [], "is_pinned": False}
    new_message["reacts"].append({"react_id": 1, "u_ids": [], "is_this_user_reacted": False})
    store["channels"][channel_id]["message"].append(new_message)

    # user/s stats updated when user sends message
    dt = int( time.time())
    stat_user_message_add(u_id, dt)
    num_msg = store['workspace']['messages'][-1]['num_messages_exist']
    store['workspace']['messages'].append({'num_messages_exist': num_msg + 1, 'time_stamp': dt})

    data_store.set(store)
    save_data()
    return {"message_id": message_id}

def message_edit_v1(token, message_id, message):

    """ Given a valid message id inside a channel, either the user that sent the 
        original message or an owner is able to edit the message.

    Args:
        token (string): auth users token that sent the message
        message_id (int): the message id of the message to be edited
        message (string): the message that will be sent and stored inside the channel

    Raises:
        AccessError: invalid token (does not exist in datastore)
        InputError: invalid message id (is not inside a channel that the user is in)
        AccessError: message id and token are valid but either the token does not refer to the original user of the message or an owner of the channel
        InputError: the message length either exceeds 1000 characters

    Returns:
        empty dictionary
    """

    store = data_store.get()


    if message == "":
        return message_remove_v1(token, message_id)

    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")
    
    if not check_valid_message_id(token, message_id):
        raise InputError(description="Invalid message id")

    if len(message) > 1000:
        raise InputError(description="Message length too long")

    for store_message in store["messages"]:
        if store_message["message_id"] != message_id:
            continue
        else: 
            channel_id = store_message["channel_id"]
            dm_id = store_message["dm_id"]

    u_id = decode_token(token)["auth_user_id"]
    if channel_id != -1:
        if not check_valid_message_perms(token, message_id) and get_permission(u_id) == 2:
            raise AccessError(description="Not permitted to edit message")

        for channel_message in store["channels"][channel_id]["message"]:
            if channel_message["message_id"] != message_id:
                continue
            else: 
                channel_message["message"] = message
    else:
        if not check_valid_message_perms(token, message_id):
            raise AccessError(description="Not permitted to edit message") 
        for dm_message in store["dms"][dm_id]["message"]:
            if dm_message["message_id"] != message_id:
                continue
            else: 
                dm_message["message"] = message
    data_store.set(store)
    save_data()
    return {}

def message_remove_v1(token, message_id):

    """ Given a valid message id inside a channel, either the user that sent the 
        original message or an owner is able to delete the message.
    
    Args:
        token (string): auth users token that sent the message
        message_id (int): the message id of the message to be edited

    Raises:
        AccessError: invalid token (does not exist in datastore)
        InputError: invalid message id (is not inside a channel that the user is in)
        AccessError: message id and token are valid but either the token does not refer to the original user of the message or an owner of the channel

    Returns:
        empty dictionary
    """

    store = data_store.get()

    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")
    
    if not check_valid_message_id(token, message_id):
        raise InputError(description="Invalid message id")

    for store_message in store["messages"]:
        if store_message["message_id"] != message_id:
            continue
        else: 
            channel_id = store_message["channel_id"]
            dm_id = store_message["dm_id"]
            # -1 channel id will mean the message is deleted (does not belong to a channel)
            


    u_id = decode_token(token)["auth_user_id"]
    if channel_id != -1:
        if not check_valid_message_perms(token, message_id) and get_permission(u_id) == 2:
            raise AccessError(description="Not permitted to edit message")
        for channel_message in store["channels"][channel_id]["message"]:
            if channel_message["message_id"] != message_id:
                continue
            else: 
                store["channels"][channel_id]["message"].remove(channel_message)
    else:
        if not check_valid_message_perms(token, message_id):
            raise AccessError(description="Not permitted to edit message")
        for dm_message in store["dms"][dm_id]["message"]:
            if dm_message["message_id"] != message_id:
                continue
            else: 
                store["dms"][dm_id]["message"].remove(dm_message)

    for store_message in store["messages"]:
        if store_message["message_id"] != message_id:
            continue
        else: 
            store_message["channel_id"] = -1
            store_message["dm_id"] = -1

    # users stats updated when user sends message
    dt = int( time.time())
    num_msg = store['workspace']['messages'][-1]['num_messages_exist']
    store['workspace']['messages'].append({'num_messages_exist': num_msg - 1, 'time_stamp': dt})

    data_store.set(store)
    save_data()
    return {}


def message_senddm_v1(token, dm_id, message):
    """ Given a valid auth user and valid dm, 
        send a message to the dm.

    Args:
        token (string): auth users token that sent the message
        dm_id (int): the id of the dm the message will be sent to
        message (string): the message that will be sent and stored inside the channel

    Raises:
        AccessError: invalid token (does not exist in datastore)
        InputError: invalid dm id 
        AccessError: auth user is not a member of the dm
        InputError: the message length either exceeds 1000 characters

    Returns:
        _type_: _description_
    """

    store = data_store.get()

    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_dm_id(dm_id):
        raise InputError(description="dm_id is not valid")

    if not check_user_in_dm(token, dm_id):
        raise AccessError(description="auth user is not a member of dm")

    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Message length too long or too short")

    auth_user_id = decode_token(token)["auth_user_id"]
    message_id = generate_message(token, -1, dm_id)

    new_message = {"message_id": message_id, "u_id": auth_user_id, "message": message, "time_sent": int( time.time()), "reacts": [], "is_pinned": False}
    new_message["reacts"].append({"react_id": 1, "u_ids": [], "is_this_user_reacted": False})
    store["dms"][dm_id]["message"].append(new_message)

    # user/s stats updated when user sends message
    dt = int( time.time())
    stat_user_message_add(auth_user_id, dt)
    num_msg = store['workspace']['messages'][-1]['num_messages_exist']
    store['workspace']['messages'].append({'num_messages_exist': num_msg + 1, 'time_stamp': dt})


    data_store.set(store)
    save_data()
    return {"message_id": message_id}

def message_react_v1(token, message_id, react_id):
    """ Given a valid message, that has not yet been reacted, react to it 

    Args:
        token (string): auth users token that sent the message
        message_id (int): id refers to message
        react_id (int): type of react, currently only react id is 1.

    Raises:
        AccessError: invalid token
        InputError: message id is invalid, or user is not in channel with the message
        InputError: invalid react id 
        InputError: already reacted, can't re-react 
    Returns:
        nothing, just empty dictionary {}
    """
    store = data_store.get()
    
    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_message_id(token, message_id):
        raise InputError(description="Invalid message id")

    # currently 1 is the only valid react id, if needed can add to the list
    if react_id not in [1]:
        raise InputError(description="Invalid react id")

    if check_react_id(token, message_id):
        raise InputError(description="Already reacted")

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
                ch_message["reacts"][0]["u_ids"].append(auth_user_id)
    else:
        # assume (correctly) that id is valid, either will be valid channel id or dm id 
        for dm_message in store["dms"][dm_id]["message"]:
            if dm_message["message_id"] == message_id:
                dm_message["reacts"][0]["u_ids"].append(auth_user_id)
    
    return {}

def message_unreact_v1(token, message_id, react_id):
    """ Given a message thats been reacted, unreact to it

    Args:
        token (string): auth users token that sent the message
        message_id (int): id refers to message
        react_id (int): type of react, currently only react id is 1.

    Raises:
        AccessError: invalid token
        InputError: message id is invalid, or user is not in channel with the message
        InputError: invalid react id 
        InputError: not yet reacted, can't unreact

    Returns:
        nothing, just empty dictionary {}
    """
    store = data_store.get()
    
    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_message_id(token, message_id):
        raise InputError(description="Invalid message id")

    # currently 1 is the only valid react id, if needed can add to the list
    if react_id not in [1]:
        raise InputError(description="Invalid react id")

    if not check_react_id(token, message_id):
        raise InputError(description="Already reacted")

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
                ch_message["reacts"][0]["u_ids"].remove(auth_user_id)
    else:
        # assume (correctly) that id is valid, either will be valid channel id or dm id 
        for dm_message in store["dms"][dm_id]["message"]:
            if dm_message["message_id"] == message_id:
                dm_message["reacts"][0]["u_ids"].remove(auth_user_id)

    return {}

def message_pin_v1(token, message_id):

    """ Given a message, a user with owner perms can pin the message

    Raises:
        AccessError: invalid token
        InputError: message id is invalid, or user is not in channel with the message
        AccessError: user does not have owners perms 
        InputError: already pinned

    Returns:
        empty dictionary {}
    """
    store = data_store.get()

    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_message_id(token, message_id):
        raise InputError(description="Invalid message id")

    if not check_valid_owner_perms(token, message_id) and get_permission(decode_token(token)["auth_user_id"]) == 2:
        raise AccessError(description="User does not have owner perms")

    if check_pin(message_id):
        raise InputError(description="Message is already pinned")

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
                ch_message["is_pinned"] = True
    else:
        for dm_message in store["dms"][dm_id]["message"]:
            if dm_message["message_id"] == message_id:
                dm_message["is_pinned"] = True

    return {}


def message_unpin_v1(token, message_id):

    """ Given a message, a user with owner perms can unpin a message that has already been pinned

    Raises:
        AccessError: invalid token
        InputError: message id is invalid, or user is not in channel with the message
        AccessError: user does not have owners perms 
        InputError: the message is not yet pinned

    Returns:
        empty dictionary {}
    """

    store = data_store.get()

    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_message_id(token, message_id):
        raise InputError(description="Invalid message id")

    if not check_valid_owner_perms(token, message_id) and get_permission(decode_token(token)["auth_user_id"]) == 2:
        raise AccessError(description="User does not have owner perms")

    if not check_pin(message_id):
        raise InputError(description="Message is not yet pinned")

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
                ch_message["is_pinned"] = False
    else:
        for dm_message in store["dms"][dm_id]["message"]:
            if dm_message["message_id"] == message_id:
                dm_message["is_pinned"] = False

    return {}

def message_sendlater_v1(token, channel_id, message, time_sent):
    """ Given a valid token, channel_id, message and time_sent the user is able to send 
        message to channel at a specific point in time.

    Args:
        token (string): auth users token that sent the message
        channel_id (int): the channel id of the channel where message is sent
        message (string): the message that will be sent and stored inside the channel
        time_sent (int): the time when the message is sent

    Raises:
        AccessError: invalid token (does not exist in datastore)
        InputError: invalid channel id (channel does not exist)
        InputError: the message length either exceeds 1000 characters or is less than 1
        InputError: the time_sent is in the past
        AccessError: the token is valid but the user is not in the channel

    Returns:
        message_id(int): message if of the message sent at specific time and can only be used after the message is sent
    """
    
    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_channel_id(channel_id):
        raise InputError(description="Invalid channel id")

    u_id = decode_token(token)["auth_user_id"]
    if not check_channel_memebers(channel_id, u_id):
        raise AccessError(description="User not in channel")

    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Message length too long or too short")

    current_time = int(datetime.datetime.now().timestamp())
    
    if time_sent < current_time:
        raise InputError(description="Time is in the past")

    wait_time = time_sent - current_time

    message_id = generate_message(token, -1, -1)

    Timer(wait_time, message_sendlater_helper, [token, message_id, message, time_sent, channel_id, -1]).start()

    return {"message_id": message_id}

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    """ Given a valid token, dm_id, message and time_sent the user is able to send 
        message to dm at a specific point in time.

    Args:
        token (string): auth users token that sent the message
        dm_id (int): the dm id of the dm where message is sent
        message (string): the message that will be sent and stored inside the dm
        time_sent (int): the time when the message is sent

    Raises:
        AccessError: invalid token (does not exist in datastore)
        InputError: invalid dm id (dm does not exist)
        InputError: the message length either exceeds 1000 characters or is less than 1
        InputError: the time_sent is in the past
        AccessError: the token is valid but the user is not in the dm

    Returns:
        message_id(int): message if of the message sent at specific time and can only be used after the message is sent
    """
    
    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_dm_id(dm_id):
        raise InputError(description="Invalid dm id")

    if not check_user_in_dm(token, dm_id):
        raise AccessError(description="User not in dm")

    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Message length too long or too short")

    current_time = int(datetime.datetime.now().timestamp())
    
    if time_sent < current_time:
        raise InputError(description="Time is in the past")

    wait_time = time_sent - current_time
    
    message_id = generate_message(token, -1, -1)

    Timer(wait_time, message_sendlater_helper, [token, message_id, message, time_sent, -1, dm_id]).start()

    return {"message_id": message_id}

def message_sendlater_helper(token, message_id, message, time_sent, channel_id, dm_id):
    store = data_store.get()

    if dm_id != -1 and store["dms"][dm_id]["dm_id"] == -1:
        data_store.set(store)
        save_data()
        return {}

    u_id = decode_token(token)['auth_user_id']

    store['messages'][message_id]['channel_id'] = channel_id
    store['messages'][message_id]['dm_id'] = dm_id

    if channel_id != -1:
        new_message = {"message_id": message_id, "u_id": u_id, "message": message, "time_sent": time_sent, "reacts": [], "is_pinned": False}
        new_message["reacts"].append({"react_id": 1, "u_ids": [], "is_this_user_reacted": False})
        store["channels"][channel_id]["message"].append(new_message)

    else: 
        new_message = {"message_id": message_id, "u_id": u_id, "message": message, "time_sent": time_sent, "reacts": [], "is_pinned": False}
        new_message["reacts"].append({"react_id": 1, "u_ids": [], "is_this_user_reacted": False})
        store["dms"][dm_id]["message"].append(new_message)

    stat_user_message_add(u_id, time_sent)
    num_msg = store['workspace']['messages'][-1]['num_messages_exist']
    store['workspace']['messages'].append({'num_messages_exist': num_msg + 1, 'time_stamp': time_sent})

    data_store.set(store)
    save_data()

    return {}