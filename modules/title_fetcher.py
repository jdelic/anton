import util
from BeautifulSoup import BeautifulSoup as soup
import requests
import commands

@commands.register(re.compile(r'http://[^ $]*'))
def fetch_title:(callback, m):
    url = m.group()

    r = requests.get(url)
    if r.status_code != requests.codes.ok:
        return

    page = soup(r.text)
    results = page.find("title")
    if results is not None:
        return "%s: %s" % (url, util.strip_html(results).decode("utf-8"))
