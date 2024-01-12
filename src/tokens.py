'''
token.py

This is a helper file for making and decoding tokens. There is a generate session,
generate token, a decode token, reset sessions and current sessions function.
These are used in auth login and register to create new tokens, and to clear the datastore.

'''
import jwt
from src.data_store import data_store

global SESSION_TRACKER
SESSION_TRACKER = 0
SECRET = 'H13BBADGER'

def generate_new_session_id():
    """Generates a new sequential session ID

    Returns:
        number: The next session ID
    """

    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER


def generate_token(user_id):
    """Generates a token using the global SECRET

    Args:
        auth_user_id ([user_id]): The username

    Returns:
        string: A token encoded string
    """

    store = data_store.get()

    session_id = generate_new_session_id()

    payload = {
        'auth_user_id': user_id, 
        'session_id': session_id
    }
    token = jwt.encode(payload, SECRET, algorithm='HS256')

    store['tokens'].append(token)
    data_store.set(store)

    return token


def decode_token(token):
    """Decodes a token string into an object of the data

    Args:
        encoded_token ([token]): The encoded token as a string

    Returns:
        Object: An object storing the body of the token encoded string
    """

    return jwt.decode(token, SECRET, algorithms=['HS256'])

def reset_sessions():
    """Resets the global sessions, for when data store is reset.

    Returns:
        Empty dictionary.
    """
    global SESSION_TRACKER
    SESSION_TRACKER = 0
    return {}


def load_session_tracker(session_tracker):
    global SESSION_TRACKER
    SESSION_TRACKER = session_tracker
