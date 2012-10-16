from base import BaseMatcher
import os
import requests
import re
import json
import times
from datetime import datetime, timedelta


NUM_REGEX = r'(?:[\s#]|^i?|\si)(\d\d\d\d?\d?)(?:[\s\.,\?!]|$)'
API_KEY = os.environ.get('SIFTER')
COMMON_HTTP_STATUS_CODES = [
    '200',
    '301', '302', '304',
    '400', '401', '403', '404',
    '500', '501', '502', '503', '504',
]


def find_ticket(number):
    if number in COMMON_HTTP_STATUS_CODES:
        return

    headers = {
        'X-Sifter-Token': API_KEY
    }
    url = 'https://unisubs.sifterapp.com/api/projects/12298/issues?q=%s'
    api = url % number
    r =  requests.get(api, headers=headers)
    data = json.loads(r.content)

    back = datetime.utcnow() - timedelta(days=90)

    for issue in data['issues']:
        if str(issue['number']) == number:
            updated = times.to_universal(issue['updated_at'])
            if updated > back:
                return format_ticket(issue)


def format_ticket(issue):
    url = "https://unisubs.sifterapp.com/issue/%s" % issue['number']
    return "%s - %s - %s" % (issue['number'], issue['subject'], url)


def parse(text):
    issues = re.findall(NUM_REGEX, text)
    return set(map(find_ticket, issues))


class SifterMatcher(BaseMatcher):

    name = 'sifter'

    def respond(self, message, user=None):
        issues = parse(message)
        if len(issues) == 0:
            return
        message = str(", ".join(issues))
        self.speak(message)
