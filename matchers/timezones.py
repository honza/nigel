import datetime
from base import BaseMatcher
from pytz import timezone
import pytz

class TimezoneMatcher(BaseMatcher):

    name = 'timezone'
    greetings = [
        'timezone',
        ''
    ]
    timezones = {
        'EST':timezone('US/Eastern'),
        'Sao Paulo': timezone('America/Sao_Paulo'),
        'San Francisco': timezone('America/Tijuana'),
    }
    fmt = '%H:%M:%S %Z%z'
    
    def respond(self, message, user=None):
        if user and user.startswith('unisubs-jenkins'):
            return

        if not message.startswith('timezone'):
            return
        now  = datetime.datetime.now()
        buffer = []
        for name,tz in self.timezones.items():
            buffer.append("%s : %s" % (name, tz.localize(now)))
        message = str("\n".join(buffer))
        self.speak(message)
