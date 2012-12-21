from base import BaseMatcher
import requests
import json
import os
from datetime import datetime

JENKINS_HOST = os.environ.get('JENKINS_HOST', None)


def get_data(name):
    url = "%s/job/%s/api/json" % (JENKINS_HOST, name)

    if not url:
        print 'no url'
        return

    r = requests.get(url)
    data = json.loads(r.content)

    last_build_url = "%sapi/json" % data['lastBuild']['url']
    r = requests.get(last_build_url)
    data = json.loads(r.content)


    time = datetime.fromtimestamp(data['timestamp'] / 1000)
    delta = datetime.now() - time
    minutes_ago = delta.seconds / 60

    return {
        'result': data['result'],
        'ago': minutes_ago,
        'url': data['url'],
        'env': name
    }


def format_message(data):
    if not data:
        return None
    return "%s, %s, Last build: %s minutes ago, %s" \
        % (data['env'], data['result'], data['ago'], data['url'])


def main(env):
    data = get_data(env)
    return format_message(data)


def get_jobs():
    url = "%s/api/json" % JENKINS_HOST
    r = requests.get(url)
    data = r.json
    return [j['name'] for j in data['jobs']]


class JenkinsMatcher(BaseMatcher):

    name = 'jenkins'

    def respond(self, message, user=None):
        if not user:
            return

        if not message.startswith('jenkins'):
            return

        jobs = get_jobs()

        messages = map(main, jobs)

        for message in messages:
            self.speak(str(message))
