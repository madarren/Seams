'''
Tests for the generation and decoding of tokens.

'''
import pytest
from src.data_store import initial_object
from src.tokens import *
from src.other import clear_v1

@pytest.fixture
def clear():
    clear_v1()


def test_string_appended(clear):
    ''' Test a token is generated into the data store. '''
    generate_token(1)
    assert len(initial_object['tokens']) == 1

def test_decoder(clear):
    ''' Test a token will can be decoded with the correct payload. '''
    token = generate_token(1)
    answer = {
        'auth_user_id': 1,
        'session_id': 1
    }
    assert decode_token(token) == answer


clear_v1()
