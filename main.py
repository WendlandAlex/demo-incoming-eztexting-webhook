import queue
from flask import Flask, abort, request, Response
import asyncio
import requests
import json
import base64
import hashlib
import hmac
import os
import time
from dotenv import load_dotenv

from hmacSHA1 import generate_hash_bytes
from in_tasks import in_queues, parse_regex
from out_tasks import out_queues, modify_group_membership, send_confirmation

load_dotenv()
test_webhook    = os.getenv('NGROK', None)
signing_key = os.getenv('WEBHOOK_SECRET_KEY', None)


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


async def dispatch_task(fromNumber=None, message=None):
    # if in_queues.get('parse_regex').enqueue(parse_regex, message=message, fromNumber=fromNumber):
    #     return Response(status=200, response='Received your text!')

    # else:
    #     return Response(status=500)

    send_confirmation_response = None

    groupNames = parse_regex(message, fromNumber, queue=False)
    if groupNames is not None:
        if modify_group_membership(fromNumber, groupNames, queue=False): 
            send_confirmation_response = send_confirmation(fromNumber, groupNames, queue=False)

    if send_confirmation_response is not None:
        return send_confirmation_response
    else:
        return Response('No valid signup group provided', status=404)

# setup flask webhook handler
app = Flask(__name__)

@app.route('/inbound_sms_received', methods=['POST'])
async def handle_sms():
    # print(request.headers)
    # print(request.json)

    try:
        message_type = request.json.get('type', None)
        print(message_type)
        if message_type != 'inbound_text.received':
            abort(404)
    except Exception as e:
        print(e)
        abort(404)

    if not validate_hmac_header(request.headers.get('X-Signature'), request.json, signing_key):
        abort(403)

    return await dispatch_task(fromNumber=request.json.get('fromNumber'), message=request.json.get('message'))
    
if __name__ == '__main__':
    app.run(port=8080)
