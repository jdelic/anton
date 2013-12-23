import util
from BeautifulSoup import BeautifulSoup as soup
import requests
import commands
import re
import HTMLParser


@commands.register(re.compile(r'https?://[^ $]*'))
def fetch_title(callback, m):
    url = m.group()

    try:
        r = requests.get(url)
    except Exception as e:  # Yeah yeah...
        print e
        return

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
        page = soup(r.text)
    except HTMLParser.HTMLParseError:
        return "Could not parse %s with BeautifulSoup. Shun the author." % url
    except TypeError:
        # This seems to be the case if r.text is, for example, an image. This can
        # still happen if a site sends a malformed Content-type header, but it
        # should be rare.
        return

    results = page.find("title")
    if results is not None:
        return util.strip_html(results).decode("utf-8")

if __name__ == '__main__':
    print fetch_title(None, re.match(r'http://[^ $]*', "foo http://google.com/ bar"))
