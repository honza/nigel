import random
from base import BaseMatcher


class VolunteerMatcher(BaseMatcher):
    dev_text = "volunteer someone"
    all_text = "volunteer a dev"
    dev_candidates = ['sjl', 'arthurdebert', 'honza', 'fernandotakai', 'nicksergeant']
    all_candidates = dev_candidates + ['cz', 'ehazlett']

    def respond(self, message, user=None):
        if self.dev_text in message.lower():
            victim = random.choice(self.dev_candidates)
            self.speak('%s is it' % victim)
        elif self.all_text in message.lower():
            victim = random.choice(self.all_candidates)
            self.speak('%s is it' % victim)
