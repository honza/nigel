Nigelbot
========

A simple IRC bot that responds to commands.  Inspired by Hubot.

Motivation
----------

Why not just use Hubot instead of writing a bot from scratch?  It's because
Hubot is implemented in CoffeeScript and runs on node.js.  The IRC adapter for
hubot is utterly broken and as we know, node.js is cancer.

Installation
------------

::

    $ virtualevn env --no-site-packages
    $ source env/bin/activate
    $ pip install -r requirements.txt

Running
-------

To have Nigel join the ``#room`` room and log traffic to ``room.log``:

::

    $ python nigel.py room room.log

License
-------

BSD, short and sweet
