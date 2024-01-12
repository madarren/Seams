'''
Tests for clear_v1.

'''

from src.data_store import initial_object
from src.other import clear_v1
from src.tokens import generate_token

def test_empty_data_store():
    ''' Test that an empty datastore stays empty.'''
    initial_object['users'] = []
    initial_object['channels'] = []
    initial_object['tokens'] = []
    clear_v1()
    assert initial_object['users'] == []
    assert initial_object['channels'] == []
    assert initial_object['tokens'] == []

def test_filled_data_store():
    ''' Test that a datastore with elements in each list is cleared.'''
    initial_object['users'] = ["string1", "string2"]
    initial_object['channels'] = ["string3", "string4"]
    generate_token(1)
    clear_v1()
    assert initial_object['users'] == []
    assert initial_object['channels'] == []
    assert initial_object['tokens'] == []
