import random
from base import BaseMatcher


class VolunteerMatcher(BaseMatcher):
    all_text = "volunteer someone"
    all_text_other = "volunteer someone else"
    dev_text = "volunteer a dev"
    dev_text_other = "volunteer another dev"

    dev_candidates = ['sjl', 'arthurdebert', 'honza', 'fernandotakai', 'nicksergeant']
    all_candidates = dev_candidates + ['cz', 'ehazlett']

    def choose(self, message, user):
        victim = None

        if self.dev_text_other in message.lower():
            while (not victim) or victim == user:
                victim = random.choice(self.dev_candidates)
            return victim

        if self.dev_text in message.lower():
            return random.choice(self.dev_candidates)

        if self.all_text_other in message.lower():
            while (not victim) or victim == user:
                victim = random.choice(self.all_candidates)
            return victim

        if self.all_text in message.lower():
            return random.choice(self.all_candidates)

    def respond(self, message, user=None):
        victim = self.choose(message, user)

        if victim:
            self.speak('%s is it' % victim)

