from base import BaseMatcher


class GreetingMatcher(BaseMatcher):

    name = 'greeter'
    greetings = [
        'all: morning',
        'all: howdy',
        'all: greetings',
        'all: hello',
        'all: hey',
        'all: hi',
        ''
    ]

    def respond(self, message, user=None):
        if message.lower() in self.greetings:
            if user:
                message = user + ": hey"
                self.speak(message)

        if message.lower() == 'all: back':
            if user:
                message = user + ": welcome back"
                self.speak(message)

        if message.lower() == 'all: lunch':
            self.speak('nom nom nom')
