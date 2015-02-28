import datetime
import json
import pprint

import redis
from scrapy import log


class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return str(o)
        else:
            return json.JSONDecoder.default(self, o)


class RedisStatsCollector(object):

    def __init__(self, crawler):
        self._dump = crawler.settings.getbool('STATS_DUMP')
        self._stats = {}
        self._job = None
        self._redis = None

    def get_value(self, key, default=None, spider=None):
        return self._stats.get(key, default)

    def get_stats(self, spider=None):
        return self._stats

    def set_value(self, key, value, spider=None):
        self._stats[key] = value
        self._flush()

    def set_stats(self, stats, spider=None):
        self._stats = stats
        self._flush()

    def inc_value(self, key, count=1, start=0, spider=None):
        d = self._stats
        d[key] = d.setdefault(key, start) + count
        self._flush()

    def max_value(self, key, value, spider=None):
        self._stats[key] = max(self._stats.setdefault(key, value), value)
        self._flush()

    def min_value(self, key, value, spider=None):
        self._stats[key] = min(self._stats.setdefault(key, value), value)
        self._flush()

    def clear_stats(self, spider=None):
        self._stats.clear()
        self._flush()

    def open_spider(self, spider):
        self._job = spider.__dict__.get('_job')
        settings = spider.crawler.settings
        self._init_redis(settings)

    def close_spider(self, spider, reason):
        self._flush()

        if self._dump:
            log.msg("Dumping Scrapy stats:\n" + pprint.pformat(self._stats), \
                spider=spider)

    def _init_redis(self, settings):
        host = settings.get('REDIS_HOST', '127.0.0.1')
        port = settings.getint('REDIS_PORT', 6379)
        self._redis = redis.StrictRedis(host=host, port=port)

    def _flush(self):
        if self._job and self._redis:
            key = 'SCRAPY_STATS_%s' % self._job
            payload = json.dumps(self._stats, cls=MyJSONEncoder)
            self._redis.set(key, payload)
