# -*- coding: utf-8 -*-

from anton import commands
import requests
from bs4 import BeautifulSoup

BROWSER_HEADERS = dict([
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
    ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'),
    ('Accept-Encoding', 'gzip,deflate,sdch'),
    ('Accept-Language', 'en-US,en;q=0.8'),
    ('Connection', 'keep-alive'),
    ('User-Agent', (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.4'
        '(KHTML, like Gecko) Chrome/22.0.1229.94 Safari/537.4'
    ))
])


@commands.register("!ud")
def urban_dictionary(callback, term):
    req = requests.get(
        'http://www.urbandictionary.com/define.php?term=%s' % term,
        headers=BROWSER_HEADERS
    )
    soup = BeautifulSoup(req.text)
    results = list(x.text for x in soup.select('.definition')[:3])
    return [
        "%s: %s" % (i + 1, definition)
        for i, definition in enumerate(results)
    ]
