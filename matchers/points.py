import os
import re
import redis
import urlparse
from datetime import datetime
from base import BaseMatcher


redis_url = os.environ.get('REDISTOGO_URL', None)

DAILY_ALLOWANCE = 10
DATE = 'latest_date'


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


def utc_str():
    return datetime.utcnow().strftime('%Y-%m-%d')


def from_utc_str(s):
    return datetime.strptime(s, '%Y-%m-%d')


class PointsMatcher(BaseMatcher):

    name = 'points'

    def get_points(self, person):
        name, gender = person

        value = r.hgetall(name)

        if not value:
            value = {
                'score': 0,
                'left': DAILY_ALLOWANCE
            }

            r.hmset(name, value)

        title = titles[gender]

        return "%s_%s" % (title, name), int(value['score'])

    def respond(self, message, user=None):
        if user not in names:
            return

        message = message.strip()

        # Update points left
        latest_date = r.get(DATE)
        now = datetime.utcnow().date()

        if not latest_date:
            latest_date = utc_str()
            r.set(DATE, latest_date)
        else:
            delta = now - from_utc_str(latest_date).date()
            if delta.days > 0:
                for person in names:
                    r.hset(person, 'left', DAILY_ALLOWANCE)

                r.set(DATE, utc_str())

        if message.startswith(('leaderboard', 'scoreboard',)):
            values = map(self.get_points, people)
            values = filter(None, values)

            if not values:
                return

            values.sort(key=lambda x: x[1])
            values.reverse()
            self.speak(", ".join(["%s: %s" % v for v in values]))
            return

        if message.startswith('quota'):
            value = r.hget(user, 'left')
            self.speak(user + ': you have %s left' % value)
            return

        res = re.findall(pattern, message)

        if not res:
            return

        u, op, value = res[0]
        value = int(value)

        if user == u:
            self.speak(user + ': lol, did you really just try to give points to yourself?')
            return

        if u not in names:
            return

        source_user_hash = r.hgetall(user)
        dest_user_hash = r.hgetall(u)

        if not source_user_hash:
            source_user_hash = {
                'score': 0,
                'left': DAILY_ALLOWANCE
            }

        if not dest_user_hash:
            dest_user_hash = {
                'score': 0,
                'left': DAILY_ALLOWANCE
            }

        if op == '+':
            if int(source_user_hash.get('left', 0)) < value:
                # Not enough points left for the day
                self.speak(user + ': not enough points left, lol')
                return

        if op == '+':
            r.hincrby(u, 'score', value)
            r.hincrby(user, 'left', value * -1)

        if op == '-':
            if int(source_user_hash.get('score', 0)) < value:
                # Not enough of own points
                self.speak(user + ': not enough score, lol')
            else:
                r.hincrby(u, 'score', value * -1)
                r.hincrby(user, 'score', value * -1)
