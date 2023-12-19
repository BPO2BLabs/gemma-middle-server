import base64
import json
import jwt

def get_alg_from_token(token):
    token_split = token.split('.')
    if len(token_split) != 3:
        raise ValueError("Invalid Token JWT")

    header_base64 = token_split[0]
    header_json = base64.urlsafe_b64decode(header_base64 + "==").decode()
    header = json.loads(header_json)
    
    return header.get('alg')

def modify_alg_in_token(token, secret_key):
    url_to_alg = {
    "http://www.w3.org/2001/04/xmldsig-more#hmac-sha256": "HS256"
    }
    token_splited = token.split('.')
    header_base64 = token_splited[0]
    payload_base64 = token_splited[1]
    payload_json = base64.urlsafe_b64decode(payload_base64 + "==").decode()
    payload = json.loads(payload_json)

    # Decode header
    header_json = base64.urlsafe_b64decode(header_base64 + "==").decode()
    header = json.loads(header_json)

    # Change algorithm if is needed
    if header['alg'] in url_to_alg:
        header['alg'] = url_to_alg[header['alg']]

    # Re-encode header and join with the rest of the token
    new_token = jwt.encode(payload, secret_key, algorithm=header['alg'], headers=header)
    
    return new_token, header['alg']

# Mapping URL to algorithm

