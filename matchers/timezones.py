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
        'PST': timezone('America/Tijuana'),
        'AST': timezone('America/Halifax'),
        'UTC': timezone('UTC')
    }

    fmt = '%H:%M:%S %Z%z'

    pattern = re.compile('tz\s+(?P<hour>[\d]{1,2})\s+(?P<timezone_name>[\w]+)')

    def respond(self, message, user=None):
        if not message.startswith('timezone') and not message.startswith('tz'):
            return

        convert_match = re.match(self.pattern, message)
        now = datetime.datetime.utcnow()

        if convert_match:
            match_dict =  convert_match.groupdict()

            if match_dict['timezone_name'] not in self.timezones.keys():
                self.speak("Timezone '%s' not found, valid ones are %s" % (",".join(self.timezones.keys())))
                return

            tz_info = self.timezones[match_dict['timezone_name']]
            hour = int(convert_match.groupdict()['hour'])
            base_date = now.replace(hour=hour, tzinfo=tz_info)
        else:
            base_date = now.replace(tzinfo=pytz.utc)

        items = []

        for name, tz in self.timezones.items():
            items.append("%s: %s" % (
                                name.ljust(10),
                                base_date.astimezone(tz).strftime(self.fmt)))

        message = str("\n".join(items))
        self.speak(message)
