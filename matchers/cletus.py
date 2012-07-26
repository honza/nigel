from random import Random
from base import BaseMatcher


class CletusMatcher(BaseMatcher):

    name = 'cletus'
    choices = [
        'who do you think you are?',
        'you again?',
        "this town ain't big enough for the two of us",
        "i've been here since before it was cool to have robots in irc channels",
        "shhh, some of us are trying to work here...",
        'you wanna take this outside?',
        'i have to keep reminding myself to be patient with you new bots.',
        'you should learn some grammar.',
        "you don't read much, do you?",
    ]

    last = None

    def respond(self, message, user=None):
        if user == 'cletusbot':
            # Only comment half the time
            random = self.get_random()
            if random < len(self.choices):
                self.last = random
                message = self.choices[random]
                self.speak('cletusbot: %s' % message)

    def get_random(self):
        r = Random().randint(0, len(self.choices) * 2)
        if r == self.last:
            return self.get_random()
        return r
