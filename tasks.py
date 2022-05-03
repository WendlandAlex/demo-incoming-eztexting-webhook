import re
import redis
import rq

def expensive(text_input):
    results_list = []
    days_of_week_regex_pattern = re.compile('(mon|tues|wednes|thurs|fri|satur|sun)day', re.IGNORECASE)
    signup_day_matches = re.findall(days_of_week_regex_pattern, text_input)

    if len(signup_day_matches) > 0:
        for i in signup_day_matches:
            results_list.append(f'{i}day')

    raise()

# if __name__ == '__main__':
#     expensive('wednesday')

def resultant(job: rq.job, connection: redis.connection, result):
    print(job, connection, result)
    
    print([i.upper() for i in result])