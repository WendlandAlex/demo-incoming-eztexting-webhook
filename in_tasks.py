import os
import re
import redis
import requests
import rq

from out_tasks import out_queues, modify_group_membership, send_confirmation

print(out_queues)

redis_conn = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
with rq.Connection(redis_conn):
    in_queues = {
        'parse_regex': rq.Queue('parse_regex')
    }

def parse_regex(message: str, fromNumber: str=None, id: str=None, queue=False):
    groupNames_list = []
    days_of_week_regex_pattern = re.compile('(mon|tues|wednes|thurs|fri|satur|sun)day', re.IGNORECASE)
    signup_day_matches = re.findall(days_of_week_regex_pattern, message)

    if len(signup_day_matches) > 0:
        for i in signup_day_matches:
            groupNames_list.append(f'{i}day')

        if len(groupNames_list) > 0:
            if queue:
                if out_queues.get('send_confirmation').enqueue(send_confirmation, fromNumber, groupNames_list): return True

            else: return groupNames_list

    else: return None

if __name__ == '__main__':
    with rq.Connection(redis_conn):
        worker = rq.Worker([in_queues.get('parse_regex')], connection=redis_conn, name='group_processing')
        worker.work()
