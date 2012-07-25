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
            message = "hey"
            if user:
                message = user + ": " + message
            self.speak(message)

