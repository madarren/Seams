'''
auth.py

This contains the auth functions. These include the login, register and logout functions
for which we log a user in, add new users (automatically log in), and log them out.
As per iteration 3, this file also includes the passwordreset functions.

'''
import re
from src.data_store import data_store
from src.error import InputError, AccessError
from src.tokens import *
from src.other import check_valid_token, hash
from src.persistence import save_data
import datetime
import smtplib
from email.mime.text import MIMEText
import random
import string

def auth_login_v1(email, password):
    """Given an email and password, generates a token to log in the user
    and returns the corresponding auth_id and the token.

    Exceptions:
        InputError if email or password is not valid.

    Args:
        string: email
        string: password

    Returns:
        dictionary containing:
            'token': string
            'auth_user_id': integer
    """
    store = data_store.get()

    # check email is registered inside datastore
    email_found = False
    for idx, user in enumerate(store["users"]):
        if user["email"] == email:
            email_found = True
            user_index = idx
            break

    if not email_found:
        raise InputError(description="Email not found")

    encrypted_password = hash(password)

    # check if password is correct
    if store["users"][user_index]["password"] != encrypted_password:
        raise InputError(description="Incorrect password")

    user_id = store["users"][user_index]["id"]
    token = generate_token(user_id)
    save_data()

    # return token and auth_user_id in json (dict) format
    return {
        'token': token,
        'auth_user_id': user_id,
        }


def auth_register_v1(email, password, name_first, name_last):
    """Given an email, password, first name and last name, create a new account
    in the data store and log them in.

    Exceptions:
        InputError if email, password, or the names are invalid.

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
    store = data_store.get()

    # Check for valid email.
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.match(regex, email):
        raise InputError(description="Invalid email")
    
    # Check for duplicate email.
    for user in store['users']:
        if user['email'] != email or user['removed'] == True:
            continue
        else:
            raise InputError(description="Duplicate email")

    # Check for valid passwword.
    if len(password) < 6:
        raise InputError(description="Invalid password length")

    # Check for valid first_name length.
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="Invalid first name length")

    # Check for valid last_name length.
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="Invalid last name length")
    
    # Create handle for user. Must be lowercase alphanumeric and max 20 characters.
    handle = ''.join(c for c in name_first if c.isalnum()) + ''.join(c for c in name_last if c.isalnum())
    handle = (handle.lower())[0:20]

    # Check if handle exists, and if so, change handle to new handle.
    k, repeat = 0, True
    handle_copy = handle
    while repeat and len(store['users']) > 0:
        repeat = False
        for user in store['users']:
            if user['handle'] == handle_copy and user['removed'] == False:
                repeat = True
                handle_copy = handle + str(k)
                k += 1
    
    handle = handle_copy

    # Find the global permission.
    dt = int(datetime.datetime.now().timestamp())
    global_perm = 2
    if len(store['users']) == 0:
        global_perm = 1
        store['workspace']['channels'].append({'num_channels_exist': 0, 'time_stamp': dt})
        store['workspace']['dms'].append({'num_dms_exist': 0, 'time_stamp': dt})
        store['workspace']['messages'].append({'num_messages_exist': 0, 'time_stamp': dt})

    # Register the new user. Done via a dictionary of their details.
    new_user = {
        'id': len(store['users']) + 1,
        'email': email,
        'password': hash(password),
        'first_name': name_first,
        'last_name': name_last,
        'handle': handle,
        'global_permission': global_perm,
        'removed': False,
        'profile_img_url': 'static/default.jpg',
        'stats': {
            'channels': [{'num_channels_joined': 0, 'time_stamp': dt}],
            'dms': [{'num_dms_joined': 0, 'time_stamp': dt}],
            'messages': [{'num_messages_sent': 0, 'time_stamp': dt}],
        },
        'secret_code': '',
    }
    store['users'].append(new_user)
    store['workspace']['num_users'] += 1
    new_id = len(store['users'])
    data_store.set(store)
    token = generate_token(new_id)
    save_data()
    return {
        'token': token,
        'auth_user_id': new_id,
    }

def auth_logout_v1(token):
    """Given an active token, removes the token from the dats store to logout the user.

    Exceptions:
        AccessError if token is invalid.

    Args:
        string: token

    Returns:
        empty dictionary.
    """
    # Check if token is valid.
    if not check_valid_token(token):
        raise AccessError(description="Invalid token")
    
    store = data_store.get()
    store['tokens'].remove(token)
    data_store.set(store)
    save_data()
    return {}

def auth_passwordreset_request_v1(email):
    """Given an email address, if the user is a registered user, sends them an email containing
    a specific secret code, that when entered in auth/passwordreset/reset, shows that the user
    trying to reset the password is the one who got sent this email. No error should be raised
    when passed an invalid email, as that would pose a security/privacy concern. When a user
    requests a password reset, they should be logged out of all current sessions.

    Exceptions:
        N/A

    Args:
        string: email

    Returns:
        empty dictionary.
    """
    reset_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    store = data_store.get()
    for user in store['users']:
        if user['email'] != email:
            continue
        else:
            user['secret_code'] = reset_code
    data_store.set(store)
    save_data()

    personal_email = 'h13badger@gmail.com'
    password = 'Comp1531'

    body = f'Here is your Verification Code for reseting your password: {reset_code}'

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From'] = personal_email
    msg['To'] = email
    msg['Subject'] = 'Seams Password Reset Code'
    reset_server = smtplib.SMTP('smtp.gmail.com', 587)
    reset_server.ehlo()
    reset_server.starttls()
    reset_server.login(personal_email, password)
    reset_server.sendmail(personal_email, email, msg.as_string())
    reset_server.quit()
    
    return {}

def auth_passwordreset_reset_v1(reset_code, new_password):
    '''Given a reset code for a user, set that user's new password to the password provided.
    Once a reset code has been used, it is then invalidated.

    Exceptions:
        InputError: reset code is invalid, or password is less than 6 characters.

    Args:
        string: reset_code
        string: new_password

    Returns:
        empty dictionary.
    """
    '''
    store = data_store.get()
    # Find the user with that reset code.
    user_found = False
    for user in store['users']:
        if user['secret_code'] != reset_code:
            continue
        else:
            user_found = True
            # Check password length.
            if len(new_password) < 6:
                raise InputError(description="Password is too short.")
            user['password'] = hash(new_password)
            break
    
    # Check if the user was found.
    if not user_found:
        raise InputError(description="Invalid reset code")
    
    data_store.set(store)
    save_data()
    return {}
