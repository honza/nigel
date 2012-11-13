import datetime
from base import BaseMatcher
from pytz import timezone
import pytz
import re


class TimezoneMatcher(BaseMatcher):

    name = 'timezone'
    greetings = [
        'timezone',
    ]
    timezones = {
        'EST':timezone('US/Eastern'),
        'Sao Paulo': timezone('America/Sao_Paulo'),
        'San Francisco': timezone('America/Tijuana'),
        'UTC': timezone('Etc/UTC'),
        'AST': timezone('America/Halifax'),
        'UTC': timezone('UTC')
    }
    fmt = '%H:%M:%S %Z%z'
    
    def respond(self, message, user=None):
        if user and user.startswith('unisubs-jenkins'):
            return

        if not message.startswith('timezone') and not message.startswith('tz'):
            return
        convert_match = re.match('tz\s+(?P<hour>[\d]{1,2})\s+(?P<timezone_name>[\w]+)', message)
        now = datetime.datetime.utcnow()
        if convert_match:
            match_dict =  convert_match.groupdict()
            if match_dict['timezone_name'] not in self.timezones.keys():
                self.speak("Timezone '%s' not found, valid ones are %s" % (",".join(self.timezones.keys())))
                return
            tz_info = self.timezones[match_dict['timezone_name']]
            # FIZME: create with the correct timezone, dammit
            base_date = datetime.datetime(year=now.year,
                                          month=now.month,
                                          day=now.day,
                                          hour=convert_match.groupdict()['hour'],
                                          tzinfo=tz_info)
        else:
            base_date = now.replace(tzinfo=pytz.utc)

        buffer = []

        for name,tz in self.timezones.items():
            buffer.append("%s : %s" % (name, base_date.astimezone(tz)))

        message = str("\n".join(buffer))
        self.speak(message)
