'''
incomplete.py

This contains the functions that are not finished but at least have some implementation done.
'''
from src.error import InputError, AccessError
from src.other import *
from src.tokens import decode_token

def notifications_get_v1(token):
    '''Return the user's most recent 20 notifications, ordered from most recent to least recent.
    
    Exceptions:
        AccessError: When token invalid

    Args:
        string: token

    Returns:
        {notifications: [{channel_id, dm_id, notification_message}]}
    '''
    # Check valid token.
    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")

    # Implement function.
    notifications = []

    return {'notifications': notifications}

def search_v1(token, query_str):
    '''Given a query string, return a collection of messages in all of the channels/DMs that
    the user has joined that contain the query (case-insensitive). There is no expected order
    for these messages.
    
    Exceptions:
        AccessError: When token invalid
        InputError: When length of query string is less than 1 or greater than 1000 characters

    Args:
        string: token
        string: query_str

    Returns:
        {messages: [{message_id, u_id, message, time_sent, reacts, is_pinned}]}
    '''
    # Check valid token.
    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")
    
    # Check valid query_str.
    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError(description="Invalid query string length.")

    # Implement function.
    search_result = []

    return {'messages': search_result}

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''og_message_id is the ID of the original message. channel_id is the channel that the message
    is being shared to, and is -1 if it is being sent to a DM. dm_id is the DM that the message is
    being shared to, and is -1 if it is being sent to a channel. message is the optional message in
    addition to the shared message, and will be an empty string '' if no message is given.
    A new message should be sent to the channel/DM identified by the channel_id/dm_id that contains
    the contents of both the original message and the optional message. The format does not matter
    as long as both the original and optional message exist as a substring within the new message. 
    Once sent, this new message has no link to the original message, so if the original message is 
    edited/deleted, no change will occur for the new message.
    
    Exceptions:
        AccessError: 
            token invalid
            the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the
                authorised user has not joined the channel or DM they are trying to share the 
                message to
        InputError: 
            both channel_id and dm_id are invalid
            neither channel_id nor dm_id are -1
            og_message_id does not refer to a valid message within a channel/DM that the authorised
                user has joined
            length of message is more than 1000 characters

    Args:
        string: token
        int: og_message_id
        string: message
        int: channel_id
        int: dm_id

    Returns:
        {shared_message_id}
    '''
    # Check valid token.
    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")
    
    # Check valid channel and dm id.
    if check_valid_channel_id(channel_id) == False and check_valid_dm_id(dm_id) == False:
        raise InputError(description="Invalid channel and dm id.")
    
    # Check one of the channel or dm id is -1.
    if channel_id != -1 and dm_id != -1:
        raise InputError(description="Invalid channel or dm id, one must be -1.")

    # Check user is in the place they want to share.
    if channel_id == -1 and check_user_in_dm(token, dm_id) == False:
        raise AccessError(description="Authorised user not in the dm.")
    if dm_id == -1 and check_channel_memebers(channel_id, decode_token(token)['auth_user_id']) == False:
        raise AccessError(description="Authorised user not in the channel.")
    
    # Check og_message_id is valid. NEEDS TO BE IMPLEMENTED
    if type(og_message_id) is int:
        og_message_id = 0

    # Check length of message is less than 1000 characters.
    if len(message) > 1000:
        raise InputError(description="Message is too long")

    return {'shared_message_id': 1}
