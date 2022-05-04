import os
import re
import redis
import requests
import rq
import json
import flask

session = requests.Session()
redis_conn = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
with rq.Connection(redis_conn):
    out_queues = {
        'send_confirmation': rq.Queue('send_confirmation')
    }

def get_groupIds_from_names(groups_list, queue=False):
    results = []
    for i in groups_list:
        response = requests.Request(
            method='GET',
            url='https://eztexting_api_endpoint.com',
            headers={'X-Authorization': 'Bearer oauthgoeshere'},
            json={'groupName': i}
            )
            # .json().get('groupId')

        response = response.prepare()

        results.append(response)

    return True

def modify_group_membership(fromNumber, groupNames, queue=False):
    groupIds = get_groupIds_from_names(groupNames)
    json_data = {"phoneNumber": fromNumber, "groupIds": groupIds}
    
    response = requests.Request(
        method='POST',
        url='https://eztexting_api_endpoint.com',
        headers={'X-Authorization': 'Bearer oauthgoeshere'},
        json=json_data
    )

    response = response.prepare()

    return True

def send_confirmation(fromNumber, groupNames: list, queue=False):
    print(fromNumber)
    print(groupNames)
    capitalized_groups = [i.capitalize() for i in groupNames]
    if len(capitalized_groups) > 1:
        capitalized_groups_string = ', '.join(capitalized_groups[:-2] + [' and '.join(capitalized_groups[-2:])])
    else:
        capitalized_groups_string = capitalized_groups[0]

        print(capitalized_groups_string)

    json_data = {'toNumbers': [fromNumber], 'message': f'Thank for for signing up for {capitalized_groups_string}!'}
    
    response = requests.Request(
        method='POST',
        url='https://eztexting_api_endpoint.com',
        headers={'X-Authorization': 'Bearer oauthgoeshere'},
        json=json_data
    )

    response = response.prepare()

    # print(response.headers, response.body)
    print(json.loads(response.body).get('message'))

    return flask.Response(json_data.get("message"), 200)

if __name__ == '__main__':
    with rq.Connection(redis_conn):
        worker = rq.Worker([out_queues.get('send_confirmation')], connection=redis_conn)
        worker.work()
