# -*- coding: utf-8 -*-

from anton import commands

import datetime
import re
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


pandora_date = re.compile(r'(\d{1,2}\.\d{1,2}\.\d{1,2})$')

class PandoraListing(object):

    def __init__(self, date):
        self.date = date
        self.menu = []


def fetch_menu():
    req = requests.get(
        'http://www.pandora100.de/bistro.html',
        headers=BROWSER_HEADERS
    )
    soup = BeautifulSoup(req.text)

    current = None
    for i in soup.select('#bistro > div:nth-of-type(2) > p'):

        i = i.text.strip()
        if not i:
            continue

        m = pandora_date.search(i)
        if m:
            if current:
                yield current
            d, m, y = map(int, m.groups()[0].split('.'))
            current = PandoraListing(datetime.date(2000 + y, m, d))

        current.menu = [i.strip() for i in i.split('+++')]

    if current:
        yield current


@commands.register("!pandora")
def pandora(callback):
    today = datetime.date.today()
    for i in fetch_menu():
        if today == i.date:
            return '\n'.join(i.menu)


if __name__ == '__main__':
    print(pandora(None))
