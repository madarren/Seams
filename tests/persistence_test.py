# import requests

# BASE_URL = f"http://localhost:8063/"

# valid_user = {'email': 'valid@email.com', 'password': 'password', 'name_first': 'firstname', 'name_last': 'lastname'}
# another_valid_user = {"email": "anothervalid@email.com", "password": "anotherpassword", "name_first": "firstname", "name_last": "lastname"}

# token_1 = requests.post(f"{BASE_URL}/auth/register/v2", json = valid_user).json()["token"]
# token_2 = requests.post(f"{BASE_URL}/auth/register/v2", json = another_valid_user).json()["token"]

# json_body = {"token": token_1, "name": "channel 1", "is_public": True}
# channel_1 = requests.post(f"{BASE_URL}/channels/create/v2", json = json_body).json()["channel_id"]

# json_body = {"token": token_1, "channel_id": channel_1, "message": "Hello World"}
# requests.post(f"{BASE_URL}/message/send/v1", json = json_body)

