import re
from base import BaseMatcher
import os
import requests
import json
import time
import hashlib
import logging
from random import Random

IMG_REGEX = r'.*(?:\.jpg|\.gif|\.png)'
API_USER = os.environ.get('SNIPT_API_USER')
API_KEY = os.environ.get('SNIPT_API_KEY')
URL = 'https://snipt.net/api/private/%s'
HEADERS = {
    'Authorization': 'ApiKey {0}:{1}'.format(API_USER, API_KEY),
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}


def save(text, author):
    """
    Saves all images found in text.  Called from Nigel.

    :param text: Text to search
    :param author: Author of message

    """
    # save imgs
    imgs = re.findall(IMG_REGEX, text, re.IGNORECASE)
    return [save_link(x, author) for x in imgs]


def save_link(text, author, tags=[]):
    """
    Post a new link to snipt.net

    :param link: Text to post
    :param author: Author (will be added as a tag)
    :param tags: Optional list of extra tags

    """
    if not API_USER or not API_KEY:
        return
    # calc hash of link to prevent duplicates
    snip_hash = hashlib.md5(text).hexdigest()
    # check for existing
    if get_snips_by_tag(snip_hash):
        logging.debug('Link already exists...')
        return False
    # add 'nigel' tag for later retrieval
    if 'nigel' not in tags:
        tags.append('nigel')
    if author:
        tags.append(author)
    tags.append(snip_hash)
    snip = {
        'title': time.time(),
        'lexer': 'text',
        'code': text,
        'public': True,
        'tags': ','.join(tags)}
    r = requests.post(URL % 'snipt/', headers=HEADERS, data=json.dumps(snip))
    if r.status_code != 201:
        logging.debug('Error saving: {0}'.format(r.text))


def get_snips_by_tag(tag):
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


def random():
    """
    Returns the content of a random snip

    :rtype: Snip content as string

    """
    snips = get_snips_by_tag('nigel')
    link = snips[Random().randint(0, len(snips)-1)]
    return str(link.get('code')) # throws exception for unicode


class GifterMatcher(BaseMatcher):

    name = 'gifter'
    request_regex = r'\.?(show\s)?(me\s)?\s?(the\s)?gif\.?'

    def respond(self, message, user=None):
        # parse and save
        save(message, user)
        # parse for request - only if direct message
        if user:
            if re.match(self.request_regex, message, re.IGNORECASE):
                message = random()
                self.speak(message)
