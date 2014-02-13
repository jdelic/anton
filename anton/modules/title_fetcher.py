import logging
from requests.exceptions import RequestException
from anton import util
from bs4 import BeautifulSoup
import requests
from anton import commands
import re
import HTMLParser


_log = logging.getLogger(__name__)


@commands.register(re.compile(r'https?://[^ $]*'))
def fetch_title(callback, m):
    url = m.group()

    try:
        # SSL verify is for pussys who think PKI works ;)
        # it also shouldn't really matter for this particular
        # module, but stops anton from failing at requesting
        # some internal websites
        r = requests.get(url, verify=False)
    except RequestException as e:
        # we catch this so it doesn't bubble up as usually someone
        # just posted a malformed URL to IRC
        return "nope, didn't get it (%s)" % str(e)

    if r.status_code != requests.codes.ok:
        return

    if not (r.headers['Content-type'].startswith('text') or
            r.headers['Content-type'].startswith('application/xml')):
        return

    # BeautifulSoup's objection to being passed something like
    # a JPG as a unicode string seems to be to raise a UnicodeEncodeError.
    # I could catch that, but it feels nasty. Mind you, so does this...
    # (test-case: "http://jacovanstaden.files.wordpress.com/2011/03/git-flow-overview.jpg")
    try:
        if r.text[:1] != '<':
            return
        page = BeautifulSoup(r.text)
    except HTMLParser.HTMLParseError:
        return "Could not parse %s with BeautifulSoup. Shun the author." % url
    except TypeError:
        # This seems to be the case if r.text is, for example, an image. This can
        # still happen if a site sends a malformed Content-type header, but it
        # should be rare.
        return

    result = page.find("title")
    if result is not None:
        title = util.strip_html(result).decode("utf-8")
        if len(title) > 200:
            title = "%s..." % title[:197]
        return title

    return "Untitled (no <title> tag found)"

if __name__ == '__main__':
    print fetch_title(None, re.match(r'http://[^ $]*', "foo http://google.com/ bar"))
