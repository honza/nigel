import random
from base import BaseMatcher


class VolunteerMatcher(BaseMatcher):
    dev_text = "volunteer someone"
    all_text = "volunteer a dev"
    dev_candidates = ['Steve', 'Arthur', 'Honza', 'Fernando', 'Nick']
    all_candidates = dev_candidates + ['Craig', 'Evan']

    def respond(self, message, user=None):
        if self.dev_text in message.lower():
            victim = random.choice(self.dev_candidates)
            self.speak('%s is it' % victim)
        elif self.all_text in message.lower():
            victim = random.choice(self.all_candidates)
            self.speak('%s is it' % victim)
