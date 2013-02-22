import os
import re
import redis
import urlparse
from base import BaseMatcher


# redis_url = os.environ.get('MYREDIS_URL', None)
redis_url = os.environ.get('REDISTOGO_URL', None)


if redis_url:
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(redis_url)
    r = redis.StrictRedis(host=url.hostname, port=url.port, db=0,
            password=url.password)
else:
    r = redis.StrictRedis()


people = [
    ('cz', 'm',),
    ('sjl', 'm',),
    ('nicksergeant', 'm',),
    ('ehazlett', 'm',),
    ('arthurdebert', 'm',),
    ('fernandotakai', 'm',),
    ('honza', 'm',),
    ('janeted', 'f',),
    ('maggie_s', 'f',),
]

titles = {
    'm': 'mr',
    'f': 'ms'
}

names = [p[0] for p in people]

pattern = re.compile("^(%s):\ (\+|\-)([0-9]+).*$" % '|'.join(names))


class PointsMatcher(BaseMatcher):

    name = 'points'

    def get_points(self, person):
        name, gender = person

        try:
            value = r.get(name)
        except redis.exceptions.ConnectionError:
            return None

        if value is None:
            value = 0
        else:
            value = int(value)

        title = titles[gender]

        return "%s_%s" % (title, name), value

    def respond(self, message, user=None):
        if user not in names:
            return

        if message.startswith(('leaderboard', 'scoreboard',)):
            values = map(self.get_points, people)
            values = filter(None, values)

            if not values:
                self.speak("heroku's redis is being a pita, sorry!")
                return

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

        try:
            stored_value = r.get(u)
        except redis.exceptions.ConnectionError:
            self.speak("heroku's redis is being a pita, sorry!")
            return

        if stored_value is None:
            stored_value = 0
        else:
            stored_value = int(stored_value)

        if op == '+':
            stored_value += int(value)
        else:
            stored_value -= int(value)

        try:
            r.set(u, str(stored_value))
        except redis.exceptions.ConnectionError:
            self.speak("heroku's redis is being a pita, sorry!")
