''' 
    persistence.py

    This contains the functions that will allow the data to persist, even after the server is restarted.
    Essentially, data will also be saved inside a file (as well as in memory).

    Contains a function that loads and saves the data. 
'''


from src.data_store import data_store
from json import dump, load
from src.tokens import SESSION_TRACKER, load_session_tracker
from src.message_helpers import MESSAGE_TRACKER, load_message_tracker

def save_data():
    
    store = data_store.get()
    data_structure = {
        "data_store": store, 
        "session_tracker": SESSION_TRACKER, 
        "message_tracker": MESSAGE_TRACKER,
    }

    with open("persisted_data.json", 'w') as File:
        dump(data_structure, File)

def load_data():

    with open('persisted_data.json', 'r') as File:
        data = load(File)
        store = data["data_store"]
        data_store.set(store)
        load_session_tracker(data["session_tracker"])
        load_message_tracker(data["message_tracker"])

