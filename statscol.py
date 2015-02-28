import json

import redis

import settings

redis_host = settings.__dict__.get('REDIS_HOST', '127.0.0.1')
redis_port = int(settings.__dict__.get('REDIS_PORT', 6379))
rc = redis.StrictRedis(host=redis_host, port=redis_port)


def get_stats(job_id):
    key = 'SCRAPY_STATS_%s' % job_id
    try:
        return json.loads(rc.get(key))
    except:
        return {}
