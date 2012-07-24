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
    $ export SIFTER=yourapikey
    $ export SNIPT_API_USER=sniptusername
    $ export SNIPT_API_KEY=sniptapikey

Running
-------

To have Nigel join the ``#room``:

::

    $ python nigel.py room

Or,

::

    $ export ROOM=room
    $ python nigel.py

You can ignore all messages from a certain user by adding this environment
variable:

::

    $ export IGNORED="user1,user2"

This is useful if you don't care about what your build server says in the
channel.

Available matchers
------------------

brb
~~~

People often say things like ``all: brb, back in 20min`` and then when they
come back they're like ``all: back``.  This matcher will track how long the
user has been gone and tell them if they overshot their estimate.

arthur's g+
~~~~~~~~~~~

You can ask Nigel if Arthur's ISP is blocking Google+ today.  It will respond
to "is g+ blocked at arthur's house today?".

sifter
~~~~~~

It will scan the room for mentions of Sifter issue numbers and reply with the
issues's title and URL.  Prefix numbers with ``#``.

sandwich
~~~~~~~~

It will respond to "make me a sandwich" and "sudo make me a sandwich".

greeter
~~~~~~~

When someone greets the room with "all: hello" and the like, nigel will
respond.

gifter
~~~~~~
It will scan for .gif, .png, and .jpg images and add them to Snipt.net.  It will also respond to "<botname>: show me the gif" with random links to saved images.

Deploying to Heroku
-------------------

::

    $ git clone git://github.com/honza/nigel.git
    $ cd nigel
    $ heroku create --stack cedar
    $ heroku config:add ROOM=room SIFTER=yourapikey SNIPT_API_USER=sniptuser SNIPT_API_KEY=sniptapikey
    $ git push heroku master
    $ heroku scale nigel=1

Credit
------

Mr. `cz <https://github.com/cz>`_ is responsible for the awesome name of this
bot.

License
-------

BSD, short and sweet
