from datetime import datetime, timedelta
import re
from base import BaseMatcher


class BrbMatcher(BaseMatcher):

    name = 'brb'
    memory = {}
    regex = r'([0-9]{1,3})min'

    def respond(self, message, user=None):
        if 'brb' in message.lower():
            matches = re.findall(self.regex, message.lower())
            if matches:
                now = datetime.now()
                due = now + timedelta(minutes=int(matches[0]))
                self.memory[user] = due
        elif 'all: back' in message.lower():
            if user in self.memory.keys():
                # Returning user
                due = self.memory[user]
                now = datetime.now()
                if now > due:
                    message = user + ": " + "You are late. :)"
                    self.speak(message)
                self.memory.pop(user)
        else:
            pass

