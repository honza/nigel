from base import BaseMatcher


class ArthurGooglePlusMatcher(BaseMatcher):

    text = "is g+ blocked at arthur's house today"
    name = 'Arthur G+'

    def respond(self, message, user=None):
        if self.text in message.lower():
            message = "Most likely."
            if user:
                message = user + ": " + message
            self.speak(message)
