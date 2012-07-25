from base import BaseMatcher


class SandwichMatcher(BaseMatcher):

    text = "make me a sandwich"
    name = "sandwich"

    def respond(self, message, user=None):
        if self.text in message.lower():
            if 'sudo' in message:
                message = "OK, fine..."
            else:
                message = "You wish"
            if user:
                message = user + ": " + message
            self.speak(message)
