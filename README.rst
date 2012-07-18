Nigelbot
========

A simple IRC bot that responds to commands.  Inspired by Hubot.  Implemented in
Python.

Motivation
----------

Why not just use Hubot instead of writing a bot from scratch?  It's because
Hubot is implemented in CoffeeScript and runs on node.js.  The IRC adapter for
hubot is utterly broken and as we know, node.js is cancer.

Installation
------------

::

    $ virtualenv env --no-site-packages
    $ source env/bin/activate
    $ pip install -r requirements.txt

Running
-------

To have Nigel join the ``#room``:

::

    $ python nigel.py room

Available matchers
------------------

* help

    This will print out a list of registered matchers.


* arthur's g+

    You can ask Nigel if Arthur's ISP is blocking Google+ today.  It will
    respond to "is g+ blocked at arthur's house today?".

* sifter

    It will scan the room for mentions of Sifter issue numbers and reply with
    the issues's title and URL.  Prefix numbers with ``#``.

* sandwich

    It will respond to "make me a sandwich" and "sudo make me a sandwich".

License
-------

BSD, short and sweet
