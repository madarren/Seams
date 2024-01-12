'''
dms.py

This contains the dm functions. These include the create, list, remove, details, leave,
and messages functions. 
'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import *
from src.message_helpers import check_react_id
from src.tokens import *
from src.user import *
from src.persistence import save_data
import datetime

def dm_create_v1(token, u_ids):
    """u_ids contains the user(s) that this DM is directed to, and will not include the creator.
    The creator is the owner of the DM. 
    name should be automatically generated based on the users that are in this DM.
    The name should be an alphabetically-sorted, comma-and-space-separated list of user handles, 
    e.g. 'ahandle1, bhandle2, chandle3'.

    Exceptions:
        AccessError if token is invalid
        InputError if any u_id in u_ids is invalid, or there are duplicate u_id's

    Args:
        string: token
        list of integer: u_ids

    Returns:
        dictionary with integer dm_id
    """
    store = data_store.get()

    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")

    check_duplicate = u_ids
    remove_duplicates = set(check_duplicate)

    if len(remove_duplicates) < len(u_ids):
        raise InputError(description="There are duplicate u_id's being entered.")

    for ids in u_ids:
        if check_auth_user_id(ids):
            continue
        else:
            raise InputError(description="Invalid u_id")
    

    dm_id = len(store['dms'])
    auth_user_id = decode_token(token)['auth_user_id']

    owner = user_profile_v1(token, auth_user_id)['user']

    # members = []
    # for u_id in u_ids:
    #     members.append(user_profile_v1(token, u_id)['user'])
    members = list(map(lambda u_id: user_profile_v1(token, u_id)["user"], u_ids))
    members.insert(0, owner)

    # list_name = []
    # for member in members:
    #     list_name.append(member['handle_str'])
    list_name = list(map(lambda member: member["handle_str"], members))

    list_name.sort()

    comma_space = ', '
    name = str(comma_space.join(list_name))
    
    new_dm = {
        'name': name,
        'dm_id': dm_id,
        'owners': owner,
        'members': members,
        'message': []
    }

    dm_store = store['dms']
    dm_store.append(new_dm)
    dt = int(datetime.datetime.now().timestamp())
    for mem in members:
        stat_user_dm_add(mem['u_id'], dt)
    num_dms = store['workspace']['dms'][-1]['num_dms_exist']
    store['workspace']['dms'].append({'num_dms_exist': num_dms + 1, 'time_stamp': dt})
    data_store.set(store)
    save_data()
    return {'dm_id': dm_id}

def dm_details_v1(token, dm_id):
    """Given a DM with ID dm_id that the authorised user is a member of,
    provide basic details about the DM.

    Exceptions:
        AccessError if token is invalid
        InputError if dm_id is invalid
        AccessError if auth user not in dm

    Args:
        string: token
        integer: dm_ids

    Returns:
        dictionary with string: name, and list of dictionaries of member details
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")

    # Check the dm exists.
    if not check_valid_dm_id(dm_id):
        raise InputError(description="Invalid dm id")

    # Check if user is part of the dm.
    if not check_user_in_dm(token, dm_id): 
        raise AccessError(description="User not in dm.")

    # Get the dm details.
    store = data_store.get()
    dms = store['dms'][dm_id]
    name = dms['name']
    members = []
    
    for member in dms['members']:
        member_id = member['u_id']
        member_info = store["users"][member_id - 1]
        member_details = {
            'u_id': member_id,
            'email': member_info['email'],
            'name_first': member_info['first_name'],
            'name_last': member_info['last_name'],
            'handle_str': member_info['handle'],
            'profile_img_url': member_info['profile_img_url']
        }
        members.append(member_details)

    return {
        'name': name,
        'members': members,
    }

def dm_list_v1(token):
    """Returns the list of DMs that the user is a member of.

    Exceptions:
        AccessError if token is invalid

    Args:
        string: token

    Returns:
        dictionary with list of dictionaries, where each dictionary contains types { dm_id, name }
    """
    store = data_store.get()

    if check_valid_token(token) != True:
        raise AccessError(description="Invalid Login session")     

    payload = decode_token(token)
    auth_user_id = payload['auth_user_id']

    dms_list = []
    for dms in store["dms"]:
        for member in dms["members"]:    
            if member['u_id'] == auth_user_id:
                dms_list.append({'dm_id': dms['dm_id'], 'name': dms['name']})            
                break
    return {'dms': dms_list}

def dm_remove_v1(token, dm_id):
    ''' This function removes a DM so all members are no longer in the DM.
    This can only be done by the owner of the DM.
    Exceptions:
        - InputError when dm_id does not refer to a valid dm.
        - AccessError when dm_id is valid and an authorised user is not the
          creator of the dm
        - AccessError when dm_id is valid and an authorised user is no longer
          in the dm.
    Args: 
        - string: token
        - integer: dm_id
        
    Returns:
        - Empty dictionary {}
    '''
    store = data_store.get()
    if not check_valid_token(token):
        raise AccessError(description="Invalid Token")

    if not check_valid_dm_id(dm_id):
        raise InputError(description="Invalid DM ID")
  
    auth_user_id = decode_token(token)["auth_user_id"] 
    if store["dms"][dm_id]["owners"]["u_id"] != auth_user_id:
        raise AccessError(description="Authorised user is not original DM creator")

    if not check_user_in_dm(token, dm_id):
        raise AccessError(description="This user is not a member of this DM")

    dt = int(datetime.datetime.now().timestamp())
    for mem in store['dms'][dm_id]['members']:
        stat_user_dm_remove(mem['u_id'], dt)
    num_dms = store['workspace']['dms'][-1]['num_dms_exist']
    store['workspace']['dms'].append({'num_dms_exist': num_dms - 1, 'time_stamp': dt})
    store["dms"][dm_id]["members"] = []
    store["dms"][dm_id]["dm_id"] = -1
   
    num_msgs = store["workspace"]["messages"][-1]["num_messages_exist"] - len(store["dms"][dm_id]["message"])
    store["workspace"]["messages"].append({"num_messages_exist": num_msgs, "time_stamp": dt})
    
    data_store.set(store)
    save_data()
    return {}

def dm_leave_v1(token, dm_id):
    """Given a DM ID, the user is removed as a member of this DM.
    The creator is allowed to leave and the DM will still exist if this happens.
    This does not update the name of the DM.

    Exceptions:
        AccessError if token is invalid
        InputError if dm_id is invalid
        AccessError if auth user is not a member of the dm

    Args:
        string: token
        integer: dm_id

    Returns:
        empty dictionary
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")
    
    # Check the dm exists.
    if not check_valid_dm_id(dm_id):
        raise InputError(description="Invalid dm id")

    # Check if user is part of the dm.
    if not check_user_in_dm(token, dm_id): 
        raise AccessError(description="User not in dm.")

    store = data_store.get()
    for member in store['dms'][dm_id]['members']:
        if member['u_id'] == decode_token(token)['auth_user_id']:
            store['dms'][dm_id]['members'].remove(member)
    dt = int(datetime.datetime.now().timestamp())
    stat_user_dm_remove(decode_token(token)['auth_user_id'], dt)
    data_store.set(store)
    save_data()
    return {}

def dm_messages_v1(token, dm_id, start):
    ''' Given a DM with ID dm_id that the authorised user is a member of, return up to 50 messages.
        Where message with index 0 is the most recent. It returns end which is start + 50, if 
        there are no more messages to return then end is -1.

        Exceptions:
        AccessError if token is invalid
        AccessError if dm_id is valid but user is not member of dm
        InputError if dm_id is invalid
        InputError if start is greater than number of dms

    Args:
        string: token
        integer: dm_id
        integer: start

    Returns:
        "messages": a list of up to 50 messages between the "start" index and "start + 50"
        "start": the starting index, the same as the paramater
        "end": the index of the last message, either "start + 50" if there are enough messages or "-1" if there are not enough
    '''

    store = data_store.get()
    
    if not check_valid_token(token):
        raise AccessError(description="Token provided not registered")

    if not check_valid_dm_id(dm_id):
        raise InputError(description="Invalid dm id")

    if not check_user_in_dm(token, dm_id):
        raise AccessError(description="User not in dm")

    total_messages = len(store["dms"][dm_id]["message"])
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
        if check_react_id(token, store["dms"][dm_id]["message"][total_messages - 1 - i]["message_id"]):
            store["dms"][dm_id]["message"][total_messages - 1 - i]["reacts"][0]["is_this_user_reacted"] = True
        else: 
            store["dms"][dm_id]["message"][total_messages - 1 - i]["reacts"][0]["is_this_user_reacted"] = False
        message_history.append(store["dms"][dm_id]["message"][total_messages - 1 - i])
        i += 1

    return {
        "messages": message_history,
        "start": start,
        "end": temp_end,
    }
