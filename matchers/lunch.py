from base import BaseMatcher


class LunchMatcher(BaseMatcher):

    name = 'lunch'

    def respond(self, message, user=None):
        if (len(message) < 20) and ('lunch' in message.lower()):
            message = user + ': enjoy'
            self.speak(message)
