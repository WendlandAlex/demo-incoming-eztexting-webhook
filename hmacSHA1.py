import base64
import json
import hashlib
import hmac
import os
from dotenv import load_dotenv

load_dotenv()
signing_key = os.getenv('WEBHOOK_SECRET_KEY', None)

def generate_hash_bytes(input, signing_key):
    if type(signing_key) is bytes:
        bytes_key = signing_key
    elif type(signing_key) is str:
        bytes_key = signing_key.encode('utf-8')
    if type(input) is dict:
        bytes_body = json.dumps(input).encode('utf-8')
    elif type(input) is str:
        bytes_body = input.encode('utf-8')
    elif type(input) is bytes:
        bytes_body = input
    else:
        raise TypeError

    return hmac.new(key=bytes_key, msg=bytes_body, digestmod=hashlib.sha1)
    