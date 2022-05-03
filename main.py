from flask import Flask, abort, request, Response
import redis
import requests
import json
import base64
import hashlib
import hmac
import os
import rq
import re
import time
from dotenv import load_dotenv

from hmacSHA1 import generate_hash_bytes

load_dotenv()
test_webhook    = os.getenv('NGROK', None)
signing_key = os.getenv('WEBHOOK_SECRET_KEY', None)
redis_conn = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
in_queue = rq.Queue('handle_sms', connection=redis_conn)
out_queues = [
    rq.Queue('send_confirmation', connection=redis_conn)
    ]

# Webhook documentation
# https://developers.eztexting.com/docs/webhooks-1
"""EZ Texting webhooks can optionally include a secret token that, \
    if included, is used as a secret key to create a HmacSHA1 hash of \
    the JSON payload, returned in an 'X-Signature' header. \
    This header can then be used to verify the callback POST \
    is coming from EZ Texting.
"""

def validate_hmac_header(header, body, signing_key: str):
    hashed_body_bytes = generate_hash_bytes(body, signing_key) # returns a hashlib object

    # compare this hash to hash sent by the remote host in the
    # 'X-Signature' header to prove they have the shared secret
    hashed_body_string = base64.b64encode(hashed_body_bytes.digest()).decode()
    
    print({
        'header': header,
        'body_hash': hashed_body_string
    })

    if header == hashed_body_string:
        return True

    return False

def send_confirmation(fromNumber, group):
    print(f'Congratulations {fromNumber}! You have signed up for {group}')

def extract_weekday_from_sms(message: str, fromNumber: str=None, id: str=None):
    days_of_week_regex_pattern = re.compile('(mon|tues|wednes|thurs|fri|satur|sun)day')
    signup_day_matches = re.findall(days_of_week_regex_pattern, message)
    
    for availability_bucket in signup_day_matches:
        out_queues[0].enqueue(send_confirmation, fromNumber, availability_bucket)

app = Flask(__name__)

@app.route('/inbound_sms_received', methods=['POST'])
def handle_sms():
    print(request.headers)
    print(request.json)

    try:
        message_type = request.json.get('type', None)
        print(message_type)
        if message_type != 'inbound_text.received':
            abort(404)
    except Exception as e:
        print(e)
        abort(404)

    is_valid = validate_hmac_header(request.headers.get('X-Signature'), request.json, signing_key)
        
    if not is_valid: abort(403)

    return Response(status=200, response=f'Received your text \"{request.json.get("message")}\"')

    
if __name__ == '__main__':
    app.run(port=8080)
