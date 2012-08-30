from base import BaseMatcher
import requests
import json
import os
from datetime import datetime


ENVS = {
    'dev': os.environ.get('JENKINS_DEV', None),
    'staging': os.environ.get('JENKINS_STAGING', None)
}


def get_data(env):
    url = ENVS[env]

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
        'env': env
    }


def format_message(data):
    if not data:
        return None
    return "Env: %s --- Status: %s --- Last build: %s minutes ago --- %s" \
        % (data['env'], data['result'], data['ago'], data['url'])


def main(env):
    data = get_data(env)
    return format_message(data)


class JenkinsMatcher(BaseMatcher):

    name = 'jenkins'

    def respond(self, message, user=None):
        if not user:
            return

        if 'jenkins dev' in message:
            message = main('dev')
        elif 'jenkins staging' in message:
            message = main('staging')
        else:
            return

        if not message:
            return

        self.speak(str(message))


if __name__ == '__main__':
    print main('dev')
