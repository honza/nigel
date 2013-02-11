import os
import re
import redis
import urlparse
from base import BaseMatcher


redis_url = os.environ.get('MYREDIS_URL', None)


if redis_url:
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(redis_url)
    r = redis.StrictRedis(host=url.hostname, port=url.port, db=0,
            password=url.password)
else:
    r = redis.StrictRedis()


people = [
    'cz',
    'sjl',
    'nicksergeant',
    'ehazlett',
    'arthurdebert',
    'fernandotakai',
    'honza',
]

pattern = re.compile("^(%s):\ (\+|\-)([0-9\.]+)$" % '|'.join(people))


def get_points(name):
    value = r.get(name)

    if value is None:
        value = 0.0
    else:
        value = float(value)

    return name, value


class PointsMatcher(BaseMatcher):

    name = 'points'

    def respond(self, message, user=None):
        if user not in people:
            return

        if message.startswith(('leaderboard', 'scoreboard',)):
            values = map(get_points, people)
            values.sort(key=lambda x: x[1])
            values.reverse()
            self.speak(", ".join(["%s: %s" % v for v in values]))
            return

        res = re.findall(pattern, message)

        if not res:
            return

        u, op, value = res[0]

        if user == u:
            return

        stored_value = r.get(u)
        if stored_value is None:
            stored_value = 0.0
        else:
            stored_value = float(stored_value)

        if op == '+':
            stored_value += float(value)
        else:
            stored_value -= float(value)

        r.set(u, str(stored_value))
