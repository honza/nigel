from base import BaseMatcher
import re


words = [
    'silly',
    'stupid',
    'dumb',
    'shut',
    'broken',
    'wake',
    'lazy',
    'screw',
    'fuck',
    'crap',
    'shit',
    'pita',
    'friggin',
    'ass',
    'fu',
]

PATTERN = re.compile('|'.join(words), re.IGNORECASE)


class SillyMatcher(BaseMatcher):

    name = 'points'
    botname = 'nigel_bot'

    def respond(self, message, user=None):
        if not message.startswith(self.botname):
            return

        if re.findall(PATTERN, message):
            self.speak(user + ': excuse me')
