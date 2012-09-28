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
        page = soup(r.text)
    except HTMLParser.HTMLParseError:
        return "Could not parse %s with BeautifulSoup. Shun the author." % url

    results = page.find("title")
    if results is not None:
        return util.strip_html(results).decode("utf-8")

if __name__ == '__main__':
    print fetch_title(None, re.match(r'http://[^ $]*', "foo http://google.com/ bar"))
