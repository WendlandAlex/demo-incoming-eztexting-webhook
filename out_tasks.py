import os
import re
import redis
import requests
import rq

session = requests.Session()
redis_conn = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
with rq.Connection(redis_conn):
    out_queues = {
        'send_confirmation': rq.Queue('send_confirmation')
    }

def get_groupIds_from_names(groups_list):
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

    print(response)

    return ['111133334','1233450235']

def modify_group_membership(fromNumber, groupNames):
    groupIds = get_groupIds_from_names(groupNames)
    json_data = {"phoneNumber": fromNumber, "groupIds": groupIds}
    
    response = requests.Request(
        method='POST',
        url='https://eztexting_api_endpoint.com',
        headers={'X-Authorization': 'Bearer oauthgoeshere'},
        json=json_data
    )

    response = response.prepare()

    print(response)

    return True

def send_confirmation(fromNumber, groupNames: list):
    modify_group_membership(fromNumber, groupNames)
    json_data = {'toNumbers': [fromNumber], 'message': f'Thank for for signing up for {" ".join(groupNames)}'}
    
    response = requests.Request(
        method='POST',
        url='https://eztexting_api_endpoint.com',
        headers={'X-Authorization': 'Bearer oauthgoeshere'},
        json=json_data
    )

    response = response.prepare()

    print(response.headers, response.body)

    return True

if __name__ == '__main__':
    with rq.Connection(redis_conn):
        worker = rq.Worker([out_queues.get('send_confirmation')], connection=redis_conn)
        worker.work()
