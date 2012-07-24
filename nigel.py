import sys
import os
import re
from datetime import datetime, timedelta
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from sifter import parse
import gifter

IGNORED_USERS = os.environ.get('IGNORED', '').split(',')


class BaseMatcher(object):
    """
    Subclass the ``BaseMatcher`` to create your own.  Register it by adding an
    instance of the subclass to ``matchers``.
    """

    def respond(self, message):
        raise NotImplementedError

    def speak(self, message):
        """
        Say something
        """
        self.brain.bot.msg(self.channel, message)


class GreetingMatcher(BaseMatcher):

    name = 'greeter'
    greetings = [
        'all: morning',
        'all: howdy',
        'all: greetings',
        'all: hello',
        'all: hey',
        'all: hi',
        ''
    ]

    def respond(self, message, user=None):
        if message.lower() in self.greetings:
            message = "hey"
            if user:
                message = user + ": " + message
            self.speak(message)


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


class SifterMatcher(BaseMatcher):

    name = 'sifter'

    def respond(self, message, user=None):
        issues = parse(message)
        if len(issues) == 0:
            return
        message = str(", ".join(issues))
        self.speak(message)


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


class ArthurGooglePlusMatcher(BaseMatcher):

    text = "is g+ blocked at arthur's house today"
    name = 'Arthur G+'

    def respond(self, message, user=None):
        if self.text in message.lower():
            message = "Most likely."
            if user:
                message = user + ": " + message
            self.speak(message)


class GifterMatcher(BaseMatcher):

    name = 'gifter'
    request_regex = r'\.?(show\s)?(me\s)?\s?(the\s)?gif\.?'

    def respond(self, message, user=None):
        # parse and save
        gifter.save(message, user)
        # parse for request - only if direct message
        if user:
            if re.match(self.request_regex, message, re.IGNORECASE):
                message = gifter.random()
                self.speak(message)


class Brain(object):
    """
    Check an incoming message against registered matchers and let the matchers
    speak into the channel.
    """

    def __init__(self, bot, matchers):
        self.bot = bot
        self.channel = None
        self.matchers = []
        map(self.register, matchers)

    def register(self, matcher):
        matcher.brain = self
        matcher.brain = self
        self.matchers.append(matcher)

    def set_channel(self, channel):
        for matcher in self.matchers:
            matcher.channel = channel
        self.channel = channel

    def handle(self, channel, message, user=None):
        for matcher in self.matchers:
            matcher.respond(message, user)


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    nickname = "nigelbot"

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)

    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]

        if not self.brain.channel:
            self.brain.set_channel(channel)

        if user in IGNORED_USERS:
            print 'ignoring message from:', user
            return

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg = msg.replace(self.nickname + ':', '')
            msg = msg.strip()
            self.brain.handle(channel, msg, user)
            return

        self.brain.handle(channel, msg, user)


class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel):
        self.channel = channel

    def buildProtocol(self, addr):
        p = LogBot()
        p.brain = Brain(p, [GreetingMatcher(), BrbMatcher(), SifterMatcher(),
                SandwichMatcher(), ArthurGooglePlusMatcher(), GifterMatcher()])
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    room = os.environ.get('ROOM')
    if not room:
        room = sys.argv[1]
    f = LogBotFactory(room)

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()
