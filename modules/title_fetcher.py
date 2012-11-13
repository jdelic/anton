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
    except Exception as e: #Yeah yeah...
        print e
        return

    if r.status_code != requests.codes.ok:
        return

    try:
        if r.text[:1] != '<': # BeautifulSoup's objection to being passed something like a JPG as a unicode string seems to be to raise a UnicodeEncodeError. I could catch that, but it feels nasty. Mind you, so does this... (test-case: "http://jacovanstaden.files.wordpress.com/2011/03/git-flow-overview.jpg")
            return
        page = soup(r.text)
    except HTMLParser.HTMLParseError:
        return "Could not parse %s with BeautifulSoup. Shun the author." % url
    except TypeError: 
        """
10:19 < james> http://www.explosm.net/db/files/Comics/Rob/help.png
10:19 < holly> exception occured:
10:19 < holly> Traceback (most recent call last):
10:19 < holly>   File "/home/holly/holly/commands.py", line 93, in chanmsg_handler
10:19 < holly>     r = command(callback, obj["message"])
10:19 < holly>   File "/home/holly/holly/commands.py", line 28, in new_fn
10:19 < holly>     return return_callback(callback, fn(callback, m))
10:19 < holly>   File "/home/holly/holly/modules/title_fetcher.py", line 22, in fetch_title
10:19 < holly>     page = soup(r.text)
10:19 < holly>   File "/home/holly/holly_virtualenv/lib/python2.6/site-packages/requests/models.py", line 824, in text
10:19 < holly>     content = str(self.content, encoding, errors='replace')
10:19 < holly> TypeError: unicode() argument 2 must be string, not None
        """
        # This seems to be the case if r.text is, for example, an image. Should really handle this better, but I don't see an obviously nicer way (parsing Content-Type? Manual check that r.text is "HTML-y"?)
        return

    results = page.find("title")
    if results is not None:
        return util.strip_html(results).decode("utf-8")

if __name__ == '__main__':
    print fetch_title(None, re.match(r'http://[^ $]*', "foo http://google.com/ bar"))
