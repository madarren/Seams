'''
user.py

This contains the user and users functions. These are the users all function, and the
user profile, setname, setemail, sethandle, uploadphoto, stats functions.
This file also contains the two admin_user functions. These are the user remove and
userpermission change functions, that remove users or change their global permissions.

'''
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import *
from src.tokens import decode_token
from src.persistence import save_data
import re
import urllib.request
from urllib.error import HTTPError, URLError
from PIL import Image

def users_all_v1(token):
    """Given an active token, returns a list of all users and their associated details.

    Exceptions:
        AccessError if token is invalid.

    Args:
        string: token

    Returns:
        dictionary with list of all active users, where each user is a dictionary of details.
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Get users and their details.
    store = data_store.get()
    users_list = []
    for member in store['users']:
        if member['removed'] == True:
            continue
        else:
            user_details = {
                'u_id': member['id'],
                'email': member['email'],
                'name_first': member['first_name'],
                'name_last': member['last_name'],
                'handle_str': member['handle'],
                'profile_img_url': member['profile_img_url']
            }
            users_list.append(user_details)
    return {'users': users_list}

def user_profile_v1(token, u_id):
    """For a valid user, returns information about
     their user_id, email, first name, last name, and handle

    Exceptions:
        AccessError if token is invalid.
        InputError if u_id is not a valid user.

    Args:
        string: token
        integer: u_id

    Returns:
        dictionary of user, where user is a dictionary of user details.
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Check u_id exists.
    if not check_auth_user_id(u_id):
        raise InputError(description="Invalid u_id")
    
    # Get the user's details.
    store = data_store.get()
    user_details = {
        'u_id': u_id,
        'email': store['users'][u_id - 1]['email'],
        'name_first': store['users'][u_id - 1]['first_name'],
        'name_last': store['users'][u_id - 1]['last_name'],
        'handle_str': store['users'][u_id - 1]['handle'],
        'profile_img_url': store['users'][u_id - 1]['profile_img_url']
    }
    return {'user': user_details}

def user_setname_v1(token, name_first, name_last):
    """Update the authorised user's first and last name

    Exceptions:
        AccessError if token is invalid.
        InputError if first and/or last name is not between 1 and 50 characters inclusive.

    Args:
        string: token
        string: name_first
        string: name_last

    Returns:
        empty dictionary
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Check for valid first_name length.
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="Invalid first name length")

    # Check for valid last_name length.
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="Invalid last name length")
    
    # Change the user's names.
    store = data_store.get()
    auth_id = decode_token(token)['auth_user_id']
    store['users'][auth_id - 1]['first_name'] = name_first
    store['users'][auth_id - 1]['last_name'] = name_last
    data_store.set(store)
    save_data()
    return {}

def user_setemail_v1(token, email):
    """Update the authorised user's email address.

    Exceptions:
        AccessError if token is invalid.
        InputError if email is not a valid email or is a duplicate email to another user.

    Args:
        string: token
        string: email

    Returns:
        empty dictionary
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Check for valid email
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.match(regex, email):
        raise InputError(description="Invalid email")

    # Check for duplicate email.
    store = data_store.get()
    auth_id = decode_token(token)['auth_user_id']
    for user in store['users']:
        if user['email'] == email and user['id'] != auth_id and user['removed'] == False:
            raise InputError(description="Email already in use")
            
    # Change the user's email.
    store['users'][auth_id - 1]['email'] = email
    data_store.set(store)
    save_data()
    return {}

def user_sethandle_v1(token, handle_str):
    """Update the authorised user's handle (i.e. display name)

    Exceptions:
        AccessError if token is invalid.
        InputError if handle is not between 3 and 20 characters inclusive. Also if it contains
            non-alphanumeric characters, or if it is already being used by another user.

    Args:
        string: token
        string: handle_str

    Returns:
        empty dictionary
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")
    
    # Check for valid handle length.
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description="Invalid handle length")

    # Check if handle is lowercase alphanumeric.
    if not handle_str.islower() or not handle_str.isalnum():
        raise InputError(description="Handle is not a lowercase alphanumeric string")
 
    # Check for duplicate handles.
    store = data_store.get()
    auth_id = decode_token(token)['auth_user_id']
    for user in store['users']:
        if user['handle'] == handle_str and user['id'] != auth_id and user['removed'] == False:
            raise InputError(description="Handle is already in use")
    
    # Change the user's handle.
    store['users'][auth_id - 1]['handle'] = handle_str
    data_store.set(store)
    save_data()
    return {}

def admin_user_remove_v1(token, u_id):
    """Given a user by their u_id, remove them from the Seams. 
    This means they should be removed from all channels/DMs, and will not be included in the list of users returned by users/all.
    Seams owners can remove other Seams owners (including the original first owner).
    Once users are removed, the contents of the messages they sent will be replaced by 'Removed user'.
    Their profile must still be retrievable with user/profile, however name_first should be 'Removed' and name_last should be 'user'.
    The user's email and handle should be reusable.
    
    Exceptions:
        AccessError: if token invalid, or auth user not a global owner.
        InputError: if u_id is invalid, or u_id is the only global owner.

    Args:
        string: token
        integer: u_id

    Returns:
        empty dictionary
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")
    
    # Check the auth user is a global owner.
    if get_permission(decode_token(token)['auth_user_id']) == 2:
        raise AccessError(description="Auth user is not a global owner")

    # Check u_id is valid.
    if not check_auth_user_id(u_id):
        raise InputError(description="Invalid u_id")
    
    # Check if u_id is the only global owner.
    store = data_store.get()
    num_ownwers = 0
    if get_permission(u_id) == 1:
        for user in store['users']:
            num_ownwers += (user['global_permission'] % 2)
    if num_ownwers == 1:
        raise InputError(description="Cannot remove only global owner")

    # Remove u_id tokens.
    for u_token in store['tokens']:
        if decode_token(u_token)['auth_user_id'] != u_id:
            continue
        else:
            store['tokens'].remove(u_token)
        
    # Remove u_id from channels.
    for channel in store['channels']:
        if u_id in channel['owners']:
            channel['owners'].remove(u_id)
        if u_id in channel['members']:
            channel['members'].remove(u_id)
    
    # Replace all content of message sent by user by "Removed user"
    for store_message in store['messages']:
        if store_message["auth_user_id"] == u_id and store_message["channel_id"] != -1:
            for channel_message in store["channels"][store_message["channel_id"]]["message"]:
                if channel_message["message_id"] != store_message["message_id"]:
                    continue 
                else:
                    channel_message["message"] = "Removed user"
        if store_message["auth_user_id"] == u_id and store_message["dm_id"] != -1:
            for dm_message in store["dms"][store_message["dm_id"]]["message"]:
                if dm_message["message_id"] != store_message["message_id"]:
                    continue
                else:
                    dm_message["message"] = "Removed user"


    # Remove from dms.
    for dm in store['dms']:
        for member in dm['members']:
            if u_id != member['u_id']:
                continue
            else:
                dm['members'].remove(member)
    
    # Change the user's removed status.
    store['users'][u_id - 1]['first_name'] = 'Removed'
    store['users'][u_id - 1]['last_name'] = 'user'
    store['users'][u_id - 1]['removed'] = True
    store['workspace']['num_users'] = store['workspace']['num_users'] - 1
    data_store.set(store)
    save_data()
    return {}

def admin_userpermission_change_v1(token, u_id, permission_id):
    """Given a user by their user ID, set their permissions to new permissions described by permission_id.

    Exceptions:
        AccessError: if token is invalid or if authorised user is not global owner.
        InputError: if u_id is invalid, u_id is the only global owner and is being demoted, 
            permission_id is invalid, or the user already has permission_id as their permission.

    Args:
        string: token
        integer: u_id
        integer: permission_id

    Returns:
        empty dictionary
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Check the auth user is a global owner.
    if get_permission(decode_token(token)['auth_user_id']) == 2:
        raise AccessError(description="Auth user is not a global owner")

    # Check u_id is valid.
    if not check_auth_user_id(u_id):
        raise InputError(description="Invalid u_id")

    # Check if u_id is the only global owner and they are being demoted.
    store = data_store.get()
    num_ownwers = 0
    if get_permission(u_id) == 1 and permission_id == 2:
        for user in store['users']:
            num_ownwers += (user['global_permission'] % 2)
    if num_ownwers == 1:
        raise InputError(description="Cannot demote only global owner")

    # Check if permission_id is valid.
    if permission_id != 1 and permission_id != 2:
        raise InputError(description="Invalid permission id value")

    # Check if user already has that permission level.
    if get_permission(u_id) == permission_id:
        raise InputError(description="User already has that permission level")

    store['users'][u_id - 1]['global_permission'] = permission_id
    data_store.set(store)
    save_data()
    return {}

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    ''' Given a URL of an image on the internet, crops the image within bounds
    (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.
    Note: the URL needs to be a non-https URL (it should just have "http://" in the URL). 
    
    Exceptions:
        AccessError: if token is invalid.
        InputError: if img_url returns HTTP status other than 200, or any other error occurs when retrieving image.
            Any of x_start, y_start, x_end, y_end are not in image dimensions.
            x_end is less than or equal to x_start, same for y.  
            If image uploaded is not a JPG.

    Args:
        string: token
        integer: x_start, y_start, x_end, y_end
        string: img_url

    Returns:
        empty dictionary
    '''
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")
    
    # Check HTTP status code and get image.
    u_id = decode_token(token)['auth_user_id']
    file_path = 'static/' + str(u_id) + '.jpg'
    try:
        urllib.request.urlretrieve(img_url, file_path)
    except (HTTPError, URLError) as error_message:
        raise InputError(description="img_url incorrect HTTP status") from error_message
    
    image_object = Image.open(file_path)

    # Check x and y dimensions. Code inspired from stackoverflow.
    start_dimesions = bool(x_start >= 0 and y_start >= 0 and x_start < x_end and y_start < y_end)
    end_dimensions = bool(x_end <= image_object.size[0] and y_end <= image_object.size[1])
    if not bool(start_dimesions and end_dimensions):
        raise InputError(description="Invalid image dimensions given.")

    # Check if jpg or jpeg.
    if not image_object.format in ('JPG', 'JPEG'):
        raise InputError(description="Image is not a jpeg or jpg.")

    cropped = image_object.crop((x_start, y_start, x_end, y_end))
    cropped.save(file_path)

    store = data_store.get()
    store['users'][u_id - 1]['profile_img_url'] = file_path
    data_store.set(store)
    save_data()
    return {}

def user_stats_v1(token):
    ''' Fetches the required statistics about this user's use of UNSW Seams.

    Exceptions:
        AccessError: if token is invalid.

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
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Get the user's stat information.
    u_id = decode_token(token)['auth_user_id']
    store = data_store.get()
    stat_info = store['users'][u_id - 1]['stats']
    
    # Calculate the user's involvement.
    chans = stat_info['channels'][-1]['num_channels_joined']
    dms = stat_info['dms'][-1]['num_dms_joined']
    msgs = stat_info['messages'][-1]['num_messages_sent']
    denominator = store['workspace']['channels'][-1]['num_channels_exist'] + store['workspace']['dms'][-1]['num_dms_exist'] + store['workspace']['messages'][-1]['num_messages_exist']
    involvement = 0
    if denominator != 0:
        involvement = min((chans + dms + msgs)/(denominator), 1)

    return {
        'user_stats': {
            'channels_joined': stat_info['channels'],
            'dms_joined': stat_info['dms'],
            'messages_sent': stat_info['messages'],
            'involvement_rate': involvement,
        }
    }

def users_stats_v1(token):
    '''Fetches the required statistics about the use of UNSW Seams.
    
    Exceptions:
        AccessError: if token is invalid.

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
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    store = data_store.get()
    num_utilizers = 0
    for user in store['users']:
        joined_ch = bool(user['stats']['channels'][-1]['num_channels_joined'] > 0)
        joined_dm = bool(user['stats']['dms'][-1]['num_dms_joined'] > 0)
        joined = bool(joined_ch or joined_dm)
        if user['removed'] == False and joined:
            num_utilizers += 1

    denominator = store['workspace']['num_users']
    utilization = (num_utilizers)/(denominator)

    return {
        'workspace_stats': {
            'channels_exist': store['workspace']['channels'],
            'dms_exist': store['workspace']['dms'],
            'messages_exist': store['workspace']['messages'],
            'utilization_rate': utilization,
        }
    }
