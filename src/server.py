'''
server.py

This file contains all the http wraps of the iteration 2 functions for Seams.
'''

import sys
import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src import config
from src.other import clear_v1
from src.auth import *
from src.channels import *
from src.channel import *
from src.user import *
from src.message import *
from src.persistence import *
from src.dms import *
from src.standup import *
from src.incomplete import *


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

@APP.route('/clear/v1', methods=['DELETE'])
def clear_v1_iter2():
    """Resets the data store to its empty state. Resets session tracker.

    Returns:
        Empty dictionary.
    """
    return dumps(clear_v1())

@APP.route("/auth/login/v2", methods = ["POST"])
def auth_login_iter2():
    """ Given an email and password, generates a token to log in the user
        and returns the corresponding auth_id and the token.
    """
    data = request.get_json()
    return dumps(auth_login_v1(data["email"], data["password"]))

@APP.route('/auth/register/v2', methods=['POST'])
def auth_register_iter2():
    """Wrap around auth_register_v1 to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: email
        string: password
        string: name_first
        string: name_last

    Returns:
        dictionary containing:
            'token': string
            'auth_user_id': integer
    """
    data = request.get_json()
    return dumps(auth_register_v1(data['email'], data['password'], data['name_first'], data['name_last']))

@APP.route('/auth/logout/v1', methods=['POST'])
def auth_logout_iter2():
    """Wrap around auth_logout_v1 to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token

    Returns:
        empty dictionary.
    """
    data = request.get_json()
    return dumps(auth_logout_v1(data['token']))


@APP.route('/users/all/v1', methods=['GET'])
def users_all_iter2():
    """Wrap around users_all_v1 to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token

    Returns:
        dictionary with list of all active users, where each user is a dictionary of user details.
    """
    token = request.args.get('token')
    return dumps(users_all_v1(token))

@APP.route('/user/profile/v1', methods=['GET'])
def user_profile_iter2():
    """Wrap around user_profile_v1 to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        integer: u_id -> must be converted to int

    Returns:
        dictionary of user, where user is a dictionary of user details.
    """
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    return dumps(user_profile_v1(token, u_id))

@APP.route('/user/profile/setname/v1', methods=['PUT'])
def user_setname_iter2():
    """Wrap around user_setname_v1 to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        string: name_first
        string: name_last

    Returns:
        empty dictionary
    """
    data = request.get_json()
    return dumps(user_setname_v1(data['token'], data['name_first'], data['name_last']))

@APP.route('/user/profile/setemail/v1', methods=['PUT'])
def user_setemail_iter2():
    """Wrap around user_setemail_v1 to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        string: email

    Returns:
        empty dictionary
    """
    data = request.get_json()
    return dumps(user_setemail_v1(data['token'], data['email']))

@APP.route('/user/profile/sethandle/v1', methods=['PUT'])
def user_sethandle_iter2():
    """Wrap around user_sethandle_v1 to support http.
    Exceptions are the same as those in backend implementation.
    
    Args:
        string: token
        string: handle_str

    Returns:
        empty dictionary
    """
    data = request.get_json()
    return dumps(user_sethandle_v1(data['token'], data['handle_str']))

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    '''
    Http wrap for channel_create_v1. Given token, channel name and setting for channel 
    accessibility. Create a channel and add the user to the channel
    '''
    data = request.get_json()
    return dumps(channels_create_v1(data['token'], data['name'], data['is_public']))

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    '''
    Http wrap for channel_join_v1. Given token and channel ID, function add a user to the
    channel given they have permission.
    '''
    data = request.get_json()
    return dumps(channel_join_v1(data['token'], data['channel_id']))

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    '''
    Http wrap for channel_leave_v1. Given token and channel ID, function remove 
    a user to the channel if they are a member of the channel.
    '''
    data = request.get_json()
    return dumps(channel_leave_v1(data['token'], data['channel_id']))

@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    '''
    Http wrap for channel_addowner_v1. Given token, channel ID and u_id, add a member 
    to the owner list
    '''
    data = request.get_json()
    return dumps(channel_addowner_v1(data['token'], data['channel_id'], data['u_id']))

@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    '''
    Http wrap for channel_removeowner_v1. Given token, channel ID and u_id, remove a member 
    from the owner list
    '''
    data = request.get_json()
    return dumps(channel_removeowner_v1(data['token'], data['channel_id'], data['u_id']))

@APP.route("/channel/messages/v2", methods = ["GET"])
def channel_messages_iter2():
    """ Given all valid channel_id and tokens, the function will return up to 50 messages 
        between the index "start" and "start + 50", as well as the start and end indices. 
        If there are not enough messages end will be returned as -1
    """

    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    start = int(request.args.get("start"))
    return dumps(channel_messages_v1(token, channel_id, start))

@APP.route("/message/send/v1", methods = ["POST"])
def message_send_iter2():
    """ Given a valid token and channel_id, a message will be sent to the channel_id from the token (auth user). The message and message_id will be 
        saved inside the channels messages database and the auth_user_id, message_id and channel_id will be saved inside the datastore. The function returns 
        the message's id.
    """
    data = request.get_json()
    return dumps(message_send_v1(data["token"], data["channel_id"], data["message"]))


@APP.route("/message/edit/v1", methods = ["PUT"])
def message_edit_iter2():
    """ Given a valid message id inside a channel that the user is a part of, either the user that sent the 
        original message or an owner is able to edit the message.
    """
    data = request.get_json()
    return dumps(message_edit_v1(data["token"], data["message_id"], data["message"]))

@APP.route("/message/remove/v1", methods = ["DELETE"])
def message_remove_iter2():
    """ Given a valid message id inside a channel, either the user that sent the 
        original message or an owner is able to delete the message.
    """
    data = request.get_json()
    return dumps(message_remove_v1(data["token"], data["message_id"]))

@APP.route("/message/react/v1", methods = ["POST"])
def message_react_iter3():
    """ Given a valid message, react to it if it has not yet been reacted
    """
    data = request.get_json()
    return dumps(message_react_v1(data["token"], data["message_id"], data["react_id"]))

@APP.route("/message/unreact/v1", methods = ["POST"])
def message_unreact_iter3():
    """ Given a valid message, unreact to it if it is currently reacted to 
    """
    data = request.get_json()
    return dumps(message_unreact_v1(data["token"], data["message_id"], data["react_id"]))

@APP.route("/message/pin/v1", methods = ["POST"])
def message_pin_iter3():
    """ Given a message, a user with owner perms can pin the message
    """
    data = request.get_json()
    return dumps(message_pin_v1(data["token"], data["message_id"]))

@APP.route("/message/unpin/v1", methods = ["POST"])
def message_unpin_iter3():
    """ Given a message, a user with owner perms can unpin a message that has already been pinned
    """
    data = request.get_json()
    return dumps(message_unpin_v1(data["token"], data["message_id"]))


@APP.route("/channel/details/v2", methods = ["GET"])
def channel_details_iter2():
    """This is a http wrap of the channel_details_v1 backend function.
    Exceptions are found in the backend.

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
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    return dumps(channel_details_v1(token, channel_id))

@APP.route("/channels/list/v2", methods = ["GET"])
def channels_list_v2():
    """This is a http wrap of the channels_list_v1 function. This function provides
    a list of all channels and associated details that the user is part of.
    Exceptions are found in the backend.

    Args:
        string: token

    Returns: 
        dictionary containing 'channels' : a list of dictionaries that contain types
    """
    token = request.args.get('token')
    return dumps(channels_list_v1(token))

@APP.route("/channels/listall/v2", methods = ["GET"])
def channels_listall_v2():
    """This is a http wrap of the channels_list_v1 function. 
    This function providesa list of all channels including private channels.
    Exceptions are found in the backend.

    Args:
        string: token

    Returns: 
        dictionary containing 'channels' : a list of dictionaries that contain types
    """
    token = request.args.get('token')
    return dumps(channels_listall_v1(token))

@APP.route("/channel/invite/v2", methods = ["POST"])
def channel_invite_iter2():
    ''' Given token, channel_id and u_id, the function invites a user to join.
    The exceptions are the same as those in the backend. 

    Args: 
        string: token
        integer: channel_id
        integer: u_id

    Returns:
        empty dictionary.
    '''

    data = request.get_json()
    return dumps(channel_invite_v1(data["token"], data["channel_id"], data["u_id"]))

@APP.route("/admin/userpermission/change/v1", methods = ["POST"])
def admin_userpermission_change_iter2():
    """Wrap around admin_userpermission_change to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        integer: u_id
        integer: permission_id

    Returns:
        empty dictionary
    """
    data = request.get_json()
    return dumps(admin_userpermission_change_v1(data['token'], data['u_id'], data['permission_id']))

@APP.route("/admin/user/remove/v1", methods = ["DELETE"])
def admin_user_remove_iter2():
    """Wrap around admin_user_remove to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        integer: u_id

    Returns:
        empty dictionary
    """
    data = request.get_json()
    return dumps(admin_user_remove_v1(data['token'], data['u_id']))

@APP.route("/dm/details/v1", methods = ["GET"])
def dms_detail():
    """Wrap around dm_details_v1 to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        integer: dm_ids

    Returns:
        dictionary with string: name, and list of dictionaries of member details
    """
    token = request.args.get("token")
    dm_id = int(request.args.get("dm_id"))
    return dumps(dm_details_v1(token, dm_id))

@APP.route("/dm/create/v1", methods = ["POST"])
def dm_create():
    """Wrap around dm_create_v1 to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        list of integer: u_ids

    Returns:
        dictionary with integer dm_id
    """
    data = request.get_json()
    return dumps(dm_create_v1(data['token'], data['u_ids']))

@APP.route("/dm/list/v1", methods = ["GET"])
def dms_list_v1_iter_2():
    """Wrap around dm_list to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token

    Returns:
        dictionary with list of dictionaries, where each dictionary contains types { dm_id, name }
    """
    token = request.args.get("token")
    return dumps(dm_list_v1(token))

@APP.route("/dm/remove/v1", methods = ['DELETE'])
def dm_remove():
    ''' Given token, and u_id, this function removes a valid DM.
    This can only be done by the owner of the DM.

    Exceptions:
        - InputError when dm_id does not refer to a valid dm.
        - AccessError when dm_id is valid and an authorised user is not the
          creator of the dm
        - AccessError when dm_id is valid and an authorised user is no longer
          in the dm.

    Args:
        string: token
        integer: u_id

    Returns:
        Empty dictionary {}
    '''
    data = request.get_json()
    return dumps(dm_remove_v1(data['token'], data['dm_id']))


@APP.route("/message/senddm/v1", methods = ["POST"])
def message_senddm_iter2():
    """ Given a valid auth user and valid dm, 
        send a message to the dm.
    """
    data = request.get_json()
    return dumps(message_senddm_v1(data["token"], data["dm_id"], data["message"]))


@APP.route("/dm/leave/v1", methods = ["POST"])
def dms_leave_iter_2():
    """Wrap around dm_leave to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        integer: dm_id

    Returns:
        empty dictionary
    """
    data = request.get_json()
    return dumps(dm_leave_v1(data['token'], data['dm_id']))

@APP.route("/dm/messages/v1", methods = ["GET"])
def dms_messages_v1():
    '''Wrap around dm_leave to support http.
    Exceptions are the same as those in backend implementation.

    Args:
        string: token
        integer: dm_id
        integer: start

    Returns:
        "messages": a list of up to 50 messages between the "start" index and "start + 50"
        "start": the starting index, the same as the paramater
        "end": the index of the last message, either "start + 50" if there are enough messages or "-1" if there are not enough
    '''
    token = request.args.get("token")
    dm_id = int(request.args.get("dm_id"))
    start = int(request.args.get("start"))
    return dumps(dm_messages_v1(token, dm_id, start))

@APP.route("/user/profile/uploadphoto/v1", methods = ["POST"])
def user_profile_uploadphoto_iter3():
    ''' Wrap around user_profile_uploadphoto_v1 to support HTTP.
    Execptions are the same as the backend implementation.

    Args:
        string: token
        integer: x_start, y_start, x_end, y_end
        string: img_url

    Returns:
        empty dictionary
    '''
    data = request.get_json()
    x_s, x_e = data['x_start'], data['x_end']
    y_s, y_e = data['y_start'], data['y_end']
    return dumps(user_profile_uploadphoto_v1(data['token'], data['img_url'], x_s, y_s, x_e, y_e))

@APP.route("/static/<path:path>")
def send_js(path):
    ''' Function for serving the profile images. '''
    return send_from_directory('', path)

@APP.route("/user/stats/v1", methods = ["GET"])
def user_stats_iter3():
    ''' Wrap around user_stats_v1 to support HTTP.
    Execptions are the same as the backend implementation.

    Args:
        string: token

    Returns:
        {
            user_stats: {
                channels_joined: [{num_channels_joined, time_stamp}],
                dms_joined: [{num_dms_joined, time_stamp}], 
                messages_sent: [{num_messages_sent, time_stamp}], 
                involvement_rate 
            }
        }
    '''
    token = request.args.get("token")
    return dumps(user_stats_v1(token))

@APP.route("/users/stats/v1", methods = ["GET"])
def users_stats_iter3():
    ''' Wrap around users_stats_v1 to support HTTP.
    Execptions are the same as the backend implementation.

    Args:
        string: token

    Returns:
        {
            workspace_stats: {
                channels_exist: [{num_channels_exist, time_stamp}],
                dms_exist: [{num_dms_exist, time_stamp}], 
                messages_exist: [{num_messages_exist, time_stamp}], 
                utilization_rate 
            }
        }
    '''
    token = request.args.get("token")
    return dumps(users_stats_v1(token))

@APP.route("/standup/start/v1", methods=["POST"])
def standup_start():
    '''
    Http wrap for standup_start_v1. Given token, channel ID and length, function start
    standup in the channel
    '''
    data = request.get_json()
    return dumps(standup_start_v1(data['token'], data['channel_id'], data['length']))

@APP.route("/standup/active/v1", methods=["GET"])
def standup_active():
    '''
    Http wrap for standup_active_v1. Given token and channel ID, function to check if
    standup is active or not
    '''
    token = request.args.get("token")
    c_id = int(request.args.get("channel_id"))
    return dumps(standup_active_v1(token, c_id))

@APP.route("/standup/send/v1", methods=["POST"])
def standup_send():
    '''
    Http wrap for standup_send_v1. Given token, channel ID and message, function store
    messages that are send during standup to the queue
    '''
    data = request.get_json()
    return dumps(standup_send_v1(data['token'], data['channel_id'], data['message']))

@APP.route("/auth/passwordreset/request/v1", methods=["POST"])
def passwordreset_request():
    '''
    Http wrap for auth_passwordreset_request_v1.
    '''
    data = request.get_json()
    return dumps(auth_passwordreset_request_v1(data['email']))

@APP.route("/auth/passwordreset/reset/v1", methods=["POST"])
def passwordreset_reset():
    '''
    Http wrap for auth_passwordreset_reset_v1.
    '''
    data = request.get_json()
    return dumps(auth_passwordreset_reset_v1(data['reset_code'], data['new_password']))

@APP.route("/message/sendlater/v1", methods = ["POST"])
def message_sendlater():
    ''' Given token, channel_id, message_id and time_sent the function sends a message at specific time in future.
    The exceptions are the same as those in the backend. 

    Args: 
        string: token
        integer: channel_id
        integer: message_id
        integer: time_sent

    Returns:
        message_id
    '''
    
    data = request.get_json()
    return dumps(message_sendlater_v1(data['token'], data['channel_id'], data['message'], data['time_sent']))

@APP.route("/message/sendlaterdm/v1", methods = ["POST"])
def message_sendlaterdm():
    ''' Given token, dm_id, message_id and time_sent the function sends a message at specific time in future.
    The exceptions are the same as those in the backend. 

    Args: 
        string: token
        integer: dm_id
        integer: message_id
        integer: time_sent

    Returns:
        message_id
    '''
    
    data = request.get_json()
    return dumps(message_sendlaterdm_v1(data['token'], data['dm_id'], data['message'], data['time_sent']))

@APP.route("/notifications/get/v1", methods = ["GET"])
def notifications_iter3():
    ''' Wrap around notifications_get_v1 to support HTTP.
    Execptions are the same as the backend implementation.

    Args:
        string: token

    Returns:
        {notifications: [{channel_id, dm_id, notification_message}]}
    '''
    token = request.args.get("token")
    return dumps(notifications_get_v1(token))

@APP.route("/search/v1", methods = ["GET"])
def search_iter3():
    ''' Wrap around search_v1 to support HTTP.
    Execptions are the same as the backend implementation.

    Args:
        string: token
        string: query_str

    Returns:
        {messages: [{message_id, u_id, message, time_sent, reacts, is_pinned}]}
    '''
    token = request.args.get("token")
    query_str = request.args.get("query_str")
    return dumps(search_v1(token, query_str))

@APP.route("/message/share/v1", methods = ["POST"])
def message_share():
    ''' Wrap around message_share_v1 to support HTTP.
    Execptions are the same as the backend implementation.

    Args:
        string: token
        int: og_message_id
        string: message
        int: channel_id
        int: dm_id

    Returns:
        {shared_message_id}
    '''
    data = request.get_json()
    return dumps(message_share_v1(data['token'], data['og_message_id'], data['message'], data['channel_id'], data['dm_id']))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    load_data()
    APP.run(port=config.port) # Do not edit this port
