'''
Test file for channel_addowner_v1, channel_removeowner_v1, 
channel/addowner/v1 (http), channel/removeowner/v1 (http)
'''

import pytest
from src.data_store import initial_object
from src.error import InputError, AccessError
from src.channel import *
from src.channels import *
from src.other import clear_v1
from src.auth import *
from src.tokens import *
import requests
from src import config

BASE_URL = config.url
valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
valid2_user = {'email': 'second@email.com', 'password': 'password', 'name_first': 'joel', 'name_last': 'embiid'}
valid3_user = {'email': 'raccooncity@city.co', 'password': 'S.T.A.R.S', 'name_first': 'Leon', 'name_last': 'Kennedy'}


@pytest.fixture
def clear():
    clear_v1()

@pytest.fixture
def user_reg_S():
    auth_register_v1('valid@email.com', 'password', 'firstname', 'lastname')
    data = auth_login_v1('valid@email.com', 'password')
    return data

@pytest.fixture
def user_reg_S2():
    auth_register_v1('xyz@world.io', 'helloWorld', 'Python', 'Snake')
    data = auth_login_v1('xyz@world.io', 'helloWorld')
    return data

@pytest.fixture
def user_reg_S3():
    auth_register_v1('raccooncity@city.co', 'S.T.A.R.S', 'Leon', 'Kennedy')
    data = auth_login_v1('raccooncity@city.co', 'S.T.A.R.S')
    return data

@pytest.fixture
def H_clear():
    requests.delete(f"{BASE_URL}/clear/v1", json = {})

@pytest.fixture
def H_user_reg_S():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def H_user_reg_S2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid2_user)
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def H_user_reg_S3():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json = valid3_user)
    assert response.status_code == 200
    return response.json()


def test_channel_addowner_invalid_token(clear, user_reg_S, user_reg_S2):
    '''
    Test if Accesserror is raised when token is invalid
    '''
    u_token = user_reg_S['token']
    u_token2 = user_reg_S2['token']
    u_id = user_reg_S2['auth_user_id']
    c_dict = channels_create_v1(u_token, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    channel_join_v1(u_token2, c_id)
    with pytest.raises(AccessError):
        channel_addowner_v1("Undefined", c_id, u_id)

    channel_addowner_v1(u_token, c_id, u_id)
    with pytest.raises(AccessError):
        channel_removeowner_v1("Undefined", c_id, u_id)
    

def test_channel_addowner_invalid_channel_id(clear, user_reg_S, user_reg_S2):
    '''
    Test if Inputerror is raised when channel ID is invalid
    '''
    u_token = user_reg_S['token']
    u_token2 = user_reg_S2['token']
    u_id2 = user_reg_S2['auth_user_id']
    c_dict = channels_create_v1(u_token, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    channel_join_v1(u_token2, c_id)
    channels = initial_object['channels'][0]
    assert channels["channel_id"] == 0
    with pytest.raises(InputError):
        channel_addowner_v1(u_token, 99999999, u_id2)

    # channel_addowner_v1(u_token, c_id, u_id)

    # with pytest.raises(InputError):
    #     channel_removeowner_v1(u_token, 88888888, u_id2)

def test_channel_owner_invalid_u_id(clear, user_reg_S, user_reg_S2):
    '''
    Test if Inputerror is raised when u_id is invalid
    '''
    u_token = user_reg_S['token']
    u_token2 = user_reg_S2['token']
    u_id = user_reg_S2['auth_user_id']
    c_dict = channels_create_v1(u_token, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    channel_join_v1(u_token2, c_id)
    with pytest.raises(InputError):
        channel_addowner_v1(u_token, c_id, 99999999)

    channel_addowner_v1(u_token, c_id, u_id)
    with pytest.raises(InputError):
        channel_removeowner_v1(u_token, c_id, 99999999)


def test_channel_addowner_member_not_found(clear, user_reg_S, user_reg_S2):
    '''
    Test if Inputerror is raised when member is not part of the channel
    '''
    u_token = user_reg_S['token']
    u_id = user_reg_S2['auth_user_id']
    c_dict = channels_create_v1(u_token, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    with pytest.raises(InputError):
        channel_addowner_v1(u_token, c_id, u_id)


def tset_channel_addowner_already_owner(clear, user_reg_S, user_reg_S2, user_reg_S3):
    '''
    Test if Inputerror is raised when adding owner who is already an owner and remove
    an owner who is not in owner list
    '''
    u_token = user_reg_S['token']
    u_token2 = user_reg_S2['token']
    u_token3 = user_reg_S3['token']
    u_id2 = user_reg_S2['auth_user_id']
    u_id3 = user_reg_S3['auth_user_id']
    c_dict = channels_create_v1(u_token, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    channel_join_v1(u_token2, c_id)
    channel_addowner_v1(u_token, c_id, u_id2)
    with pytest.raises(InputError):
        channel_addowner_v1(u_token, c_id, u_id2)

    channel_join_v1(u_token3, c_id)
    with pytest.raises(InputError):
        channel_removeowner_v1(u_token, c_id, u_id3)

def test_channel_removeowner_only_onwer(clear, user_reg_S):
    '''
    Test if Inputerror is raised when removing the only owner in the channel
    '''
    u_token = user_reg_S['token']
    u_id = user_reg_S['auth_user_id']
    c_dict = channels_create_v1(u_token, 'SeamEgg', False)
    c_id = c_dict["channel_id"]
    with pytest.raises(InputError):
        channel_removeowner_v1(u_token, c_id, u_id)

    
def test_channel_addowner_no_permission(clear, user_reg_S, user_reg_S2, user_reg_S3):
    '''
    Test if Accesserror is raised when a normal user add an owner and remove an owner
    '''
    u_token = user_reg_S['token']
    c_dict = channels_create_v1(u_token, 'SeamEgg', True)
    c_id = c_dict["channel_id"]
    u_token2 = user_reg_S2['token']
    channel_join_v1(u_token2, c_id)
    u_token3 = user_reg_S3['token']
    u_id3 = user_reg_S3['auth_user_id']
    channel_join_v1(u_token3, c_id)
    with pytest.raises(AccessError):
        channel_addowner_v1(u_token2, c_id, u_id3)

    channel_addowner_v1(u_token, c_id, u_id3)
    with pytest.raises(AccessError):
        channel_removeowner_v1(u_token2, c_id, u_id3)

def test_H_channel_owner_public(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Success case of adding owner and remove owner (Public)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200

    token = H_user_reg_S2['token']
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={H_user_reg_S2['auth_user_id']}")
    user_details = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['owner_members'][1]['u_id'] == user_details['user']['u_id']
    assert c_data['all_members'][1]['u_id'] == user_details['user']['u_id']

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={H_user_reg_S['auth_user_id']}")
    user_details2 = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['owner_members'][0]['u_id'] == user_details2['user']['u_id']
    assert c_data['all_members'][0]['u_id'] == user_details2['user']['u_id']
    assert c_data['all_members'][1]['u_id'] == user_details['user']['u_id']

def test_H_channel_owner_private(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Success case of adding owner and remove owner (Private)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Egg", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S['auth_user_id']})
    assert response.status_code == 200

    token = H_user_reg_S['token']
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={H_user_reg_S['auth_user_id']}")
    user_details = user_resp.json()
    user_resp = requests.get(f"{BASE_URL}/user/profile/v1?token={token}&u_id={H_user_reg_S2['auth_user_id']}")
    user_details2 = user_resp.json()
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert c_data['owner_members'][1]['u_id'] == user_details['user']['u_id']
    assert c_data['all_members'][0]['u_id'] == user_details2['user']['u_id']
    assert c_data['all_members'][1]['u_id'] == user_details['user']['u_id']

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200
    response = requests.get(f"{BASE_URL}/channel/details/v2?token={token}&channel_id={c_id}")
    assert response.status_code == 200
    c_data = response.json()
    assert len(c_data['owner_members']) == 1
    assert c_data['all_members'][0]['u_id'] == user_details2['user']['u_id']
    assert c_data['all_members'][1]['u_id'] == user_details['user']['u_id']

def test_H_channel_owner_invalid_token(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test if Accesserror is raised when token is invalid
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": "Undefined", "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 403

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": "Undefined", "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 403

def test_H_channel_owner_invalid_channel_id(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test if Inputerror is raised when channel ID is invalid
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": 88888888, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 400

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": 88888888, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 400

def test_H_channel_owner_u_id_not_found(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test if Inputerror is raised when u_id is not valid user
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": 99999999})
    assert response.status_code == 400

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": 99999999})
    assert response.status_code == 400

def test_H_channel_owner_user_not_in_channel(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test if Inputerror is raised when adding owner who is not in the channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 400

def test_H_channel_owner_list(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test if Inputerror is raised when adding a member already an owner and removing an owner
    but not in the list
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 400

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S3['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 400

def test_H_channel_owner_only_owner(H_clear, H_user_reg_S):
    '''
    Test if Inputerror is raised when removing the only owner in the channel
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S['auth_user_id']})
    assert response.status_code == 400

def test_H_channel_insufficient_permission(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test if Accesserror is raised when a normal member tried to add an owner or remove an owner
    '''

    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S3['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 403

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 403

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200


###################################################################################################
###################################################################################################


def test_H_global_owner_member_addowner(H_clear, H_user_reg_S, H_user_reg_S2):
    '''
    Test global owner able to add owner if they are a member
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S['auth_user_id']})
    assert response.status_code == 200

def test_H_non_member_cannot_add_owner(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test if Accesserror if raised when a non member tried to add owner
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S3['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 403

def test_H_global_owner_nonmember_cant_addowner_public(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test if AccessError is raised when global owner tried to add owner but not a member of the channel
    (Public)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S3['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 403

def test_H_global_owner_nonmember_cant_addowner_private(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test if AccessError is raised when global owner tried to add owner but not a member of the channel
    (Private)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Egg", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 403


def test_H_global_owner_member_removeonwer(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test global owner able to remove owner if they are a member
    (Public)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200

def test_H_nonmember_cannot_removeowner(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test if Accesserror is raised when a non member remove an owner
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S3['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 403

def test_H_member_cannot_removeowner(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test if Accesserror is raised when a normal member tried to remove an owner
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S3['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S3['token'], "channel_id": c_id, "u_id": H_user_reg_S2['auth_user_id']})
    assert response.status_code == 403

def test_H_member_cannot_addowner(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test if Accesserror is raised when a normal member add an owner
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S['token'], "name": "Seam_Apple", "is_public": True})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/join/v2", json={"token": H_user_reg_S3['token'], "channel_id": c_id})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 403


def test_H_global_owner_removeowner_private(H_clear, H_user_reg_S, H_user_reg_S2, H_user_reg_S3):
    '''
    Test global owner able to remove owner if they are a member
    (Private)
    '''
    response = requests.post(
        f"{BASE_URL}/channels/create/v2", json={"token": H_user_reg_S2['token'], "name": "Seam_Egg", "is_public": False})
    assert response.status_code == 200
    c_id = response.json()['channel_id']

    response = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/invite/v2", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/addowner/v1", json={"token": H_user_reg_S2['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200

    response = requests.post(
        f"{BASE_URL}/channel/removeowner/v1", json={"token": H_user_reg_S['token'], "channel_id": c_id, "u_id": H_user_reg_S3['auth_user_id']})
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json = {})
