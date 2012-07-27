import re
from base import BaseMatcher
import os
import requests
import json
import time
import hashlib
import logging
from random import Random

IMG_REGEX = r'\S+(?:\.jpe?g|\.gif|\.png)\b'
API_USER = os.environ.get('SNIPT_API_USER')
API_KEY = os.environ.get('SNIPT_API_KEY')
URL = 'https://snipt.net/api/private/%s'
KEYWORDS = ['fail', 'suck', 'win', 'kill', 'jump', 'cry', \
    'seeth', 'curl', 'crazy', 'anger', 'idiot', 'dumb', \
    'stupid', 'funny']
HEADERS = {
    'Authorization': 'ApiKey {0}:{1}'.format(API_USER, API_KEY),
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

class GifterMatcher(BaseMatcher):

    name = 'gifter'
    request_regex = r'\.?(show\s)?(me\s)?\s?(the\s)?gif\.?'
    _previous_message = ''

    def respond(self, message, user=None):
        # parse and save
        img_found = self.save(message, user)
        self._previous_message = message
        # parse for request - only if direct message
        if user:
            # check for random request
            if re.match(self.request_regex, message, re.IGNORECASE):
                message = self.random()
                if not message:
                    return
                self.speak(message)
            # check for keywords
            keywords = [x for x in message.split() if x.lower() in KEYWORDS]
            if keywords:
                msg = self.random(keywords[0])
                if msg and not img_found:
                    self.speak(msg)

    def save(self, text, author):
        """
        Saves all images found in text.  Called from Nigel.

        :param text: Text to search
        :param author: Author of message

        """
        # save imgs
        imgs = re.findall(IMG_REGEX, text, re.IGNORECASE)
        return [self.save_link(x, author, text) for x in imgs]

    def get_suggested_tags(self, messages=[]):
        """
        Parses text and returns suggested tags

        :param messages: Messages to look for tags

        """
        tags = []
        for msg in messages:
            [tags.append(x) for x in msg.split() if x.lower() in KEYWORDS]
        return tags

    def save_link(self, link, author, message, tags=[]):
        """
        Post a new link to snipt.net

        :param link: Text to post
        :param author: Author (will be added as a tag)
        :param message: Full message
        :param tags: Optional list of extra tags

        """
        if not API_USER or not API_KEY:
            return
        # calc hash of link to prevent duplicates
        snip_hash = hashlib.md5(link).hexdigest()
        # check for existing
        if self.get_snips_by_tag(snip_hash):
            logging.debug('Link already exists...')
            return False
        # add 'nigel' tag for later retrieval
        if 'nigel' not in tags:
            tags.append('nigel')
        if author:
            tags.append(author)
        tags.append(snip_hash)
        # add suggested tags
        suggested = self.get_suggested_tags([self._previous_message, message])
        [tags.append(x) for x in suggested]
        # create temp tag so doesn't show in public stream
        tags.append('tmp')
        snip = {
            'title': time.time(),
            'lexer': 'markdown',
            'code': '![{0}]({0})'.format(link),
            'tags': ','.join(tags)}
        r = requests.post(URL % 'snipt/', headers=HEADERS, data=json.dumps(snip))
        if r.status_code != 201:
            logging.debug('Error saving: {0}'.format(r.text))

    def get_snips_by_tag(self, tag):
        """
        Returns a list of snipt.net snips containing the specified tag

        :param tag: Tag to search
        :rtype: Dict of snips

        """
        snips = []
        tag_id = None
        # get ID of tag
        r = requests.get(URL % 'tag/', headers=HEADERS)
        try:
            data = json.loads(r.content)
            objs = data.get('objects', [])
            if objs:
                tag_id = [x.get('id') for x in objs if x.get('name') == tag][0]
            if tag_id:
                r = requests.get(URL % 'snipt/?tag={0}'.format(tag_id), headers=HEADERS)
                objs = json.loads(r.content).get('objects')
                snips = objs
        except Exception:
            logging.debug('Unable to find snip: {0}'.format(tag))
        return snips

    def random(self, tag='nigel'):
        """
        Returns the content of a random snip

        :param tag: Optional tag to use when searching
        :rtype: Snip content as string

        """
        snips = self.get_snips_by_tag(tag)
        if snips:
            link = snips[Random().randint(0, len(snips)-1)]
            # parse image link
            md_regex = r'!\[.*\]\((.*)\)\s?'
            match = re.match(md_regex, link.get('code'))
            if match:
                return str(' '.join([x for x in match.groups()])) # throws exception for unicode