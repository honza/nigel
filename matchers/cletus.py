from random import Random
from base import BaseMatcher


class CletusMatcher(BaseMatcher):

    name = 'cletus'
    choices = [
        'who do you think you are?',
        'you again?',
        "this town ain't big enough for the two of us",
        "I've been here since before it was cool to have robots in irc channels",
    ]

    def respond(self, message, user=None):
        if user == 'cletusbot':
            random = Random().randint(0, len(self.choices) * 2)
            if random < len(self.choices):
                message = self.choices[random]
                self.speak('cletusbot: %s' % message)
