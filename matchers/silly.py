from base import BaseMatcher
import re


words = [
    'silly',
    'stupid',
    'dumb',
    'shut',
    'broken',
    'wake',
    'lazy'
]

PATTERN = re.compile('|'.join(words))


class SillyMatcher(BaseMatcher):

    name = 'points'
    botname = 'nigel_bot'

    def respond(self, message, user=None):
        if not message.startswith(self.botname):
            return

        if re.findall(PATTERN, message):
            self.speak(user + ': excuse me')
