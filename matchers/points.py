import os
import re
import redis
from base import BaseMatcher


redis_url = os.environ.get('MYREDIS_URL', None)

if redis_url:
    r = redis.StrictRedis(redis_url)
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

    return "%s: %s" % (name, value)


class PointsMatcher(BaseMatcher):

    name = 'points'

    def respond(self, message, user=None):
        if message.startswith(('leaderboard', 'scoreboard',)):
            msg = ", ".join(map(get_points, people))
            self.speak(msg)
            return

        res = re.findall(pattern, message)

        if not res:
            return

        user, op, value = res[0]

        stored_value = r.get(user)
        if stored_value is None:
            stored_value = 0.0
        else:
            stored_value = float(stored_value)

        if op == '+':
            stored_value += float(value)
        else:
            stored_value -= float(value)

        r.set(user, str(stored_value))
