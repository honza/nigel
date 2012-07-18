import time
import sys
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from sifter import parse


matchers = []


class BaseMatcher(object):
    """
    Subclass the ``BaseMatcher`` to create your own.  Register it by adding an
    instance of the subclass to ``matchers``.
    """

    def matches(self, message, user):
        """
        Return ``True`` is a match was found.
        """
        raise NotImplementedError

    def speak(self, message, brain, channel, user):
        """
        Say something
        """
        brain.bot.msg(channel, message)


class SifterMatcher(BaseMatcher):

    name = 'sifter'

    def matches(self, message, user):
        issues = parse(message)
        return len(issues) != 0

    def speak(self, message, brain, channel, user):
        issues = parse(message)
        message = str(", ".join(issues))
        brain.bot.msg(channel, message)


matchers.append(SifterMatcher())


class SandwichMatcher(BaseMatcher):

    text = "make me a sandwich"
    name = "sandwich"

    def matches(self, message, user):
        return self.text in message.lower()

    def speak(self, message, brain, channel, user):
        if 'sudo' in message:
            message = "OK, fine..."
        else:
            message = "You wish"
        if user:
            message = user + ": " + message
        brain.bot.msg(channel, message)


matchers.append(SandwichMatcher())


class ArthurGooglePlusMatcher(BaseMatcher):

    text = "is g+ blocked at arthur's house today"
    name = 'Arthur G+'

    def matches(self, message, user):
        return self.text in message.lower()

    def speak(self, message, brain, channel, user):
        message = "Most likely."
        if user:
            message = user + ": " + message
        brain.bot.msg(channel, message)


matchers.append(ArthurGooglePlusMatcher())


class HelpMatcher(BaseMatcher):

    name = 'help'

    def matches(self, message, user):
        return user and message.startswith('help')

    def speak(self, message, brain, channel, user):
        message = user + ": registered matchers: " + \
                ", ".join([m.name for m in matchers])
        brain.bot.msg(channel, message)


matchers.append(HelpMatcher())


class Brain(object):
    """
    Check an incoming message against registered matchers and let the matchers
    speak into the channel.
    """

    def __init__(self, bot):
        self.bot = bot

    def handle(self, channel, message, user=None):
        for matcher in matchers:
            if matcher.matches(message, user):
                matcher.speak(message, self, channel, user)
                break


class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""
    
    nickname = "nigelbot"
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" % 
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % 
                        time.asctime(time.localtime(time.time())))
        self.logger.close()


    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        
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
            self.logger.log("<%s> %s" % (self.nickname, msg))
            return

        self.brain.handle(channel, msg)

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))


class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = LogBot()
        p.brain = Brain(p)
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
    f = LogBotFactory(sys.argv[1], sys.argv[2])

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()
