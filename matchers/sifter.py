from base import BaseMatcher
import os
import requests
import re
import json


NUM_REGEX = r'(?:[\s#]|^)(\d\d\d\d?\d?)(?:[\s\.,\?!]|$)'
API_KEY = os.environ.get('SIFTER')


def find_ticket(number):
    headers = {
        'X-Sifter-Token': API_KEY
    }
    url = 'https://unisubs.sifterapp.com/api/projects/12298/issues?q=%s'
    api = url % number
    r =  requests.get(api, headers=headers)
    data = json.loads(r.content)

    for issue in data['issues']:
        if str(issue['number']) == number:
            return format_ticket(issue)


def format_ticket(issue):
    url = "https://unisubs.sifterapp.com/issue/%s" % issue['number']
    return "%s - %s - %s" % (issue['number'], issue['subject'], url)


def parse(text):
    issues = re.findall(NUM_REGEX, text)
    return map(find_ticket, issues)


class SifterMatcher(BaseMatcher):

    name = 'sifter'

    def respond(self, message, user=None):
        issues = parse(message)
        if len(issues) == 0:
            return
        message = str(", ".join(issues))
        self.speak(message)
