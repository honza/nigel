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
